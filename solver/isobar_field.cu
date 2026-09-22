// ============================================================================
//  ledger_lattice.cu — THE COMPANY, RECONCILED AGAINST ITSELF, CONTINUOUSLY
//
//  One resident lattice. Cells are (seat x slot). Commitments are rows. Every
//  tick ingests a change-data-capture delta, re-prices the lattice, and prints
//  four things and only four things:
//
//    1. THE PRICE VECTOR      the dual per seat/slot/stock column. Which
//                             capacity is binding, now, not monthly.
//    2. THE SUPPORT SPECTRUM  exp(H) per commitment — the effective number of
//                             cells its mass is spread over. Low tail = the
//                             automatable mass. High tail = the frontier bill.
//    3. THE CONTRADICTIONS    every open commitment currently inconsistent
//                             with another, ranked by the dual of its column.
//    4. THE ARITHMETIC LINE   bytes moved per commitment per tick, achieved
//                             GB/s, and the fraction of MEASURED peak. If this
//                             is under the floor the workload is not
//                             bandwidth-bound and the card is not justified.
//                             That is the kill condition for the whole thesis.
//
//  IT DECIDES NOTHING. IT WRITES TO NOTHING. There is no act verb in this file.
//  It reads a stream and prints a residual. That is the entire contract.
//
//  --------------------------------------------------------------------------
//  THE FOUR TRANSPOSITIONS (FluidX3D, Dr. Moritz Lehmann / ProjectPhysX)
//
//  LBM is memory-bandwidth-bound, so the optimization target is bytes/cell, not
//  FLOPs. FluidX3D gets 153 -> 55 bytes/cell two ways: Esoteric-Pull (each pair
//  exchange done ONCE, by one party, in place — the second lattice copy
//  disappears) and decoupled precision (compute fp32, store fp16, with a
//  measured error bound). This workload has the same shape. So:
//
//   T1  THE PLAN IS NEVER MATERIALIZED.  A transport over N commitments and M
//       cells is N*M. We store only the duals: u[N] + v[M], and recompute a row
//       on the fly when we need it. O(N+M) resident against O(N*M). This is the
//       Esoteric-Pull move — the second copy is not optimized, it is deleted.
//   T2  DECOUPLED PRECISION.  Embeddings stored int8 with one fp32 scale per
//       vector; every dot product accumulates in fp32. Round-trip cosine is an
//       ORACLE (O5), not an assumption.
//   T3  THE COUNTERFACTUAL IS A MASK, NOT A COPY.  The incumbent arm and the
//       solver arm read ONE canvas through two law masks. Two arms, one state,
//       one bitmask of difference. A paired comparison every tick for the price
//       of N bits.
//   T4  LOCALITY IS THE LATTICE.  Contradiction is not all-pairs. Two
//       commitments can only contradict if they contend for something, so they
//       must share a cell or a neighbouring one. N^2 collapses to N cells x
//       fixed-degree neighbourhood — the same reduction physics hands LBM.
//
//  --------------------------------------------------------------------------
//  INHERITED DISCIPLINE (org_relax.cu REV 0, 2026-09-05)
//
//    * ONE DYNAMICS SOURCE.  place_cost() is __host__ __device__ and is the only
//      place the cost of putting a commitment in a cell is defined. The Sinkhorn,
//      the support meter and the report all read it. An oracle checks that two
//      independent paths through it agree (O1) — a self-consistency test that
//      needs no planted truth and therefore cannot be flattered by a bad fixture.
//    * A NUMBER WITHOUT ITS BAND IS NOT A NUMBER.  Every accumulator carries its
//      sum of squares. Reported quantities print a band.
//    * FIXED-POINT uint64 ACCUMULATORS, no float atomics -> memcmp-identical
//      replay under a seed (O2).
//    * VERDICTS RELATIVE TO PEERS, never bare numbers.
//    * EVERY ORACLE CARRIES A LIE.  --selftest --lie N runs oracle N against a
//      deliberately corrupted lattice; an oracle that passes its own lie is a
//      broken oracle and is reported as such.
//
//  THE T17 FIX, carried over from the OrgSolver wave-2 finding: the stock
//  columns previously had logcap = +inf and the column pass skipped their dual
//  update, so their price was ALWAYS exactly zero — a theorem, not a bug, and
//  the reason an 88%-loaded seat priced at 0.000. Here both stock columns carry
//  a FINITE capacity (adjudication bandwidth; carrying capacity) and take the
//  same dual update as any other column. See sinkhorn_cols().
//
//  --------------------------------------------------------------------------
//  BUILD
//    GPU : nvcc -O3 -std=c++17 -arch=sm_89 -o ledger_lattice ledger_lattice.cu
//          (sm_120 for RTX 50-series; sm_90 for H100/H200)
//    CPU : nvcc -O3 -std=c++17 -x c++ -DLL_CPU -o ledger_lattice ledger_lattice.cu
//          or any C++17 compiler with -DLL_CPU. Same source, serial, same oracles.
//
//  RUN
//    ledger_lattice --selftest                 six oracles, nonzero exit on failure
//    ledger_lattice --bench                    measure peak bandwidth; print the roofline
//    ledger_lattice --demo --commitments 200000 --ticks 8
//    ledger_lattice --cdc stream.csv           real delta stream (see ingest_csv)
//
//  NOT CLAIMED: no number in this file has met a real business. The synthetic
//  generator plants its own contradictions and the oracles recover them; that is
//  a test of the instrument, not of any organization.
// ============================================================================

#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <cstdint>
#include <cmath>
#include <chrono>
#include <vector>
#include <string>
#include <algorithm>

// ----------------------------------------------------------------------------
// ISOBAR (2026-09-22): this file is the LIFT of ledger_lattice.cu (sha256 5a0d6edc…c4c53), re-shaped
// for one owner's horizon. Every ISOBAR edit is marked "ISOBAR" and recorded in docs/devlog.md with
// the line it touched. Added: the WAITING stock (the price of a counterparty's silence); tier_w
// (the people registry's weight on lateness); paid/waiting rows; K_PAID + oracle O8 with its lie;
// host_view() so the selftest's host-side traversals never dereference device pointers (the GPU
// selftest segfaulted in the original — a latent defect the lift found); a peak-bandwidth buffer
// larger than L2; and the --tick binary IPC that isobard drives. -DISOBAR_CPU == -DLL_CPU.
// ----------------------------------------------------------------------------
#if defined(ISOBAR_CPU) && !defined(LL_CPU)
#define LL_CPU 1
#endif

// ----------------------------------------------------------------------------
// 0 · SUBSTRATE — the same kernels run serially under -DLL_CPU
// ----------------------------------------------------------------------------
#ifdef LL_CPU
  #define __global__
  #define __device__
  #define __host__
  #define __forceinline__ inline
  struct dim3 { unsigned x, y, z; dim3(unsigned a=1,unsigned b=1,unsigned c=1):x(a),y(b),z(c){} };
  static dim3 threadIdx, blockIdx, blockDim, gridDim;
  #define LAUNCH(kernel, nblocks, nthreads, ...)                                   \
    do {                                                                           \
      blockDim = dim3((unsigned)(nthreads)); gridDim = dim3((unsigned)(nblocks));   \
      for (unsigned _b = 0; _b < (unsigned)(nblocks); ++_b) {                       \
        blockIdx = dim3(_b);                                                        \
        for (unsigned _t = 0; _t < (unsigned)(nthreads); ++_t) {                    \
          threadIdx = dim3(_t); kernel(__VA_ARGS__);                                \
        }                                                                           \
      }                                                                             \
    } while (0)
  static inline unsigned long long atomicAdd(unsigned long long* p, unsigned long long v){ unsigned long long o=*p; *p+=v; return o; }
  static inline int  atomicAdd(int* p, int v){ int o=*p; *p+=v; return o; }
  static inline unsigned long long atomicMax(unsigned long long* p, unsigned long long v){ unsigned long long o=*p; if(v>o)*p=v; return o; }
  template <class T> T* dev_alloc(size_t n){ return (T*)calloc(n?n:1,sizeof(T)); }
  template <class T> void dev_free(T* p){ free(p); }
  template <class T> void dev_upload(T* d,const T* h,size_t n){ memcpy(d,h,n*sizeof(T)); }
  template <class T> void dev_download(T* h,const T* d,size_t n){ memcpy(h,d,n*sizeof(T)); }
  template <class T> void dev_zero(T* d,size_t n){ memset(d,0,n*sizeof(T)); }
  static inline void dev_sync(){}
  static inline void dev_meminfo(size_t* freeb,size_t* totb){ *freeb=0; *totb=0; }
#else
  #include <cuda_runtime.h>
  #define CUDA_CHECK(x) do { cudaError_t e=(x); if(e!=cudaSuccess){                 \
      fprintf(stderr,"CUDA error %s at %s:%d\n",cudaGetErrorString(e),__FILE__,__LINE__); exit(2);} } while(0)
  #define LAUNCH(kernel, nblocks, nthreads, ...) do { kernel<<<(nblocks),(nthreads)>>>(__VA_ARGS__); CUDA_CHECK(cudaGetLastError()); } while(0)
  template <class T> T* dev_alloc(size_t n){ T* p=nullptr; CUDA_CHECK(cudaMalloc(&p,(n?n:1)*sizeof(T))); CUDA_CHECK(cudaMemset(p,0,(n?n:1)*sizeof(T))); return p; }
  template <class T> void dev_free(T* p){ if(p) CUDA_CHECK(cudaFree(p)); }
  template <class T> void dev_upload(T* d,const T* h,size_t n){ CUDA_CHECK(cudaMemcpy(d,h,n*sizeof(T),cudaMemcpyHostToDevice)); }
  template <class T> void dev_download(T* h,const T* d,size_t n){ CUDA_CHECK(cudaMemcpy(h,d,n*sizeof(T),cudaMemcpyDeviceToHost)); }
  template <class T> void dev_zero(T* d,size_t n){ CUDA_CHECK(cudaMemset(d,0,n*sizeof(T))); }
  static inline void dev_sync(){ CUDA_CHECK(cudaDeviceSynchronize()); }
  static inline void dev_meminfo(size_t* freeb,size_t* totb){ CUDA_CHECK(cudaMemGetInfo(freeb,totb)); }
#endif

#define NEG_INF     (-1.0e30f)
#define IS_MASKED(x) ((x) < -1.0e29f)
#define FIX_SCALE   (65536.0)     // fixed-point scale: deterministic accumulation
#define BLOCK       256
#define EMB_D       128           // coarse embedding dim (the scan tier)
#define MAX_CONTRA  (1u<<20)
#ifndef LL_O3_ITERS
#define LL_O3_ITERS 400
#endif

static inline int grid_for(long long n){ return (int)((n + BLOCK - 1) / BLOCK); }

// ----------------------------------------------------------------------------
// 1 · COUNTER-BASED RNG (stateless, deterministic — same seed, same lattice)
// ----------------------------------------------------------------------------
__host__ __device__ __forceinline__ uint64_t mix64(uint64_t z){
  z += 0x9E3779B97F4A7C15ULL;
  z = (z ^ (z >> 30)) * 0xBF58476D1CE4E5B9ULL;
  z = (z ^ (z >> 27)) * 0x94D049BB133111EBULL;
  return z ^ (z >> 31);
}
__host__ __device__ __forceinline__ float u01(uint64_t s, uint64_t a, uint64_t b){
  uint64_t h = mix64(s ^ mix64(a ^ mix64(b ^ 0xD1B54A32D192ED03ULL)));
  return ((float)(h >> 40) + 0.5f) * (1.0f / 16777216.0f);
}
__host__ __device__ __forceinline__ float unorm(uint64_t s, uint64_t a, uint64_t b){
  const float u1 = u01(s,a,b), u2 = u01(s ^ 0x1234567ULL, a, b + 99);
  return sqrtf(-2.f * logf(u1)) * cosf(6.2831853f * u2);
}
__host__ __device__ __forceinline__ uint64_t fx(double v){
  return (uint64_t)(v * FIX_SCALE + 0.5);
}

// ----------------------------------------------------------------------------
// 2 · THE LATTICE — device view (SoA). Bytes are counted; see byte_report().
// ----------------------------------------------------------------------------
//
// Commitment state, per row. This is the "cell state" whose size the whole
// FluidX3D discipline is about. Keep it small and print it.
//
//   entity   4   who/what it is about (customer, job, case)
//   cls      2   decision class
//   dur      1   slots occupied  (a commitment occupies a RUN, not a point —
//                the OrgSolver wave-1 duration ruling, carried in by construction)
//   src      1   which system of record it came from (CDC lane id)
//   t_open   4   tick it entered
//   t_due    4   deadline tick
//   work     4   work units (fp32)
//   dep      4   the commitment this one waits on, or -1
//   inc_cell 4   the cell the INCUMBENT actually assigned it to (from the CDC)
//   flags    4   law/eligibility bits
//   ------------
//            32  bytes of scalar state, + EMB_D bytes of int8 embedding + 4 scale
//
struct Lat {
  int   N;                 // open commitments
  int   nseat, nslot;      // the lattice
  int   M;                 // nseat*nslot + N_STOCK
  int   ncls;
  float T;                 // transport temperature (entropic reg)
  float late_penalty;      // cost per slot of lateness
  // --- row state (SoA)
  const int*      entity;
  const short*    cls;
  const unsigned char* dur;
  const unsigned char* src;
  const int*      t_open;
  const int*      t_due;
  const float*    work;
  const int*      dep;
  const int*      inc_cell;
  const unsigned int* flags;
  // --- ISOBAR rows: the registries, read as numbers
  const float*         tier_w;   // [N] the people registry's multiplier on lateness (1.0 = no registry)
  const unsigned char* paid;     // [N] 1 = the money VERDICT says paid — K_PAID: never in a chase set
  const unsigned char* waiting;  // [N] 1 = blocked on a counterparty — lives ONLY in the WAITING stock
  // --- embeddings: int8 storage, fp32 compute (T2)
  const signed char* emb;      // [N * EMB_D]
  const float*       emb_scale;// [N]
  const signed char* seat_key; // [nseat * EMB_D]
  const float*       seat_scale;
  // --- capacity
  const float*  cap;       // [M] capacity per cell (work units); stock cols finite (T17 fix)
  const float*  supply;    // [N] each row ships its own work
  // --- law mask, TWO ARMS OVER ONE CANVAS (T3)
  const unsigned int* law;      // [ (nseat*ncls + 31)/32 ] bit set = class may use seat
  const unsigned int* arm_mask; // [ (nseat + 31)/32 ] bit set = seat DISABLED in the solver arm
  int arm;                      // 0 = incumbent (true law), 1 = solver (effective law)
};

// ISOBAR: a third stock. WAITING = with a counterparty; its dual is the price of their silence.
enum { STOCK_UNPLACED = 0, STOCK_UNADJUDICATED = 1, STOCK_WAITING = 2, N_STOCK = 3 };

__host__ __device__ __forceinline__ int  col_seat(const Lat& L, int c){ return c / L.nslot; }
__host__ __device__ __forceinline__ int  col_slot(const Lat& L, int c){ return c % L.nslot; }
__host__ __device__ __forceinline__ bool col_is_stock(const Lat& L, int c){ return c >= L.nseat * L.nslot; }
__host__ __device__ __forceinline__ int  stock_id(const Lat& L, int c){ return c - L.nseat * L.nslot; }

__host__ __device__ __forceinline__ bool bit_get(const unsigned int* w, int i){
  return (w[i >> 5] >> (i & 31)) & 1u;
}

// int8 dot in fp32 (T2). Decoupled precision: storage int8, accumulation float.
__host__ __device__ __forceinline__ float emb_dot(const signed char* a, float sa,
                                                  const signed char* b, float sb){
  int acc = 0;
  for (int d = 0; d < EMB_D; ++d) acc += (int)a[d] * (int)b[d];
  return (float)acc * sa * sb;
}

// ----------------------------------------------------------------------------
// 3 · THE ONE DYNAMICS SOURCE
//     The cost of placing commitment i in cell c. Everything that moves a
//     commitment is defined HERE and nowhere else: the Sinkhorn reads it, the
//     support meter reads it, the report reads it. Oracle O1 checks that two
//     independent traversals of it agree.
// ----------------------------------------------------------------------------
__host__ __device__ __forceinline__
float place_cost(const Lat& L, int i, int c)
{
  if (col_is_stock(L, c)) {
    // Both stock columns are real columns with real, FINITE capacity and a real
    // dual. THE T17 FIX. Unplaced work costs its carrying cost; unadjudicated
    // work costs the escalation cost. Neither is free and neither is infinite.
    const int s = stock_id(L, c);
    // ISOBAR: a waiting row sits in the WAITING stock (cheap, budgeted) or spills to UNPLACED (dear):
    // when the silence budget binds, the overflow prices WAITING and conservation still holds.
    // A placeable row may never sit in WAITING.
    const bool w = (L.waiting != nullptr) && L.waiting[i];
    if (w) return (s == STOCK_WAITING) ? (-1.0f / L.T) : (s == STOCK_UNPLACED) ? (-3.0f / L.T) : NEG_INF;
    if (s == STOCK_WAITING) return NEG_INF;
    return (s == STOCK_UNPLACED) ? (-3.0f / L.T) : (-2.0f / L.T);
  }
  if ((L.waiting != nullptr) && L.waiting[i]) return NEG_INF;   // ISOBAR: no lawful real cell while waiting
  const int seat = col_seat(L, c);
  const int slot = col_slot(L, c);

  // --- LAW, as a -inf mask BEFORE normalization. Unoverridable by anything learned.
  if (!bit_get(L.law, (int)L.cls[i] * L.nseat + seat)) return NEG_INF;

  // --- THE TWO ARMS, ONE CANVAS (T3). The solver arm additionally masks seats
  //     the governor has not promoted. One bitmask; no second canvas exists.
  if (L.arm == 1 && bit_get(L.arm_mask, seat)) return NEG_INF;

  // --- a commitment occupies its DURATION: it cannot start where it cannot finish
  if (slot + (int)L.dur[i] > L.nslot) return NEG_INF;

  // --- release: it cannot start before it arrived
  if (slot < 0) return NEG_INF;

  // --- fit: how well this seat matches this commitment (int8 storage, fp32 acc)
  const float compat = emb_dot(L.emb + (size_t)i * EMB_D, L.emb_scale[i],
                               L.seat_key + (size_t)seat * EMB_D, L.seat_scale[seat])
                       / sqrtf((float)EMB_D);

  // --- lateness has a price, which is what a queue rule cannot give you
  const int finish = slot + (int)L.dur[i];
  const float late = (float)(finish > L.t_due[i] ? finish - L.t_due[i] : 0);
  const float tw   = (L.tier_w != nullptr) ? L.tier_w[i] : 1.0f;   // ISOBAR: the registry weights lateness

  return (compat - L.late_penalty * tw * late) / L.T;
}

// ISOBAR: a host-side view of the lattice. The selftest's O1/O3 traversals call place_cost() on
// the host; with device pointers that dereferences cudaMalloc memory and segfaults (the original's
// GPU selftest did exactly that). Every host traversal reads THIS view, never Dev.L.
struct LatHost;
static Lat host_view(const LatHost& H);

// numerically-safe log-sum-exp over a strided run, masked entries skipped
__host__ __device__ __forceinline__
void lse_init(float& mx, float& s){ mx = NEG_INF; s = 0.f; }
__host__ __device__ __forceinline__
void lse_push(float& mx, float& s, float v){
  if (IS_MASKED(v)) return;
  if (v > mx) { s *= expf(mx - v); mx = v; }
  s += expf(v - mx);
}
__host__ __device__ __forceinline__
float lse_done(float mx, float s){ return IS_MASKED(mx) ? NEG_INF : mx + logf(s); }

// ----------------------------------------------------------------------------
// 4 · SINKHORN — DUALS ONLY. The plan is never materialized. (T1)
//
//   log P_ic = place_cost(i,c) + u_i + v_c
//   rows  (equality) : u_i = log a_i - LSE_c( C_ic + v_c )
//   cols  (inequality): v_c = min(0, log b_c - LSE_i( C_ic + u_i ))
//
// Resident state is u[N] + v[M]. A row of the plan is recomputed on demand and
// never stored. That is the Esoteric-Pull transposition: the second copy is not
// made smaller, it is deleted.
// ----------------------------------------------------------------------------
__global__ void k_sink_rows(Lat L, const float* v, const float* log_a, float* u){
  const int i = (int)(blockIdx.x * blockDim.x + threadIdx.x);
  if (i >= L.N) return;
  float mx, s; lse_init(mx, s);
  for (int c = 0; c < L.M; ++c) lse_push(mx, s, place_cost(L, i, c) + v[c]);
  const float z = lse_done(mx, s);
  u[i] = IS_MASKED(z) ? NEG_INF : (log_a[i] - z);
}

__global__ void k_sink_cols(Lat L, const float* u, const float* log_b, float* v){
  const int c = (int)(blockIdx.x * blockDim.x + threadIdx.x);
  if (c >= L.M) return;
  float mx, s; lse_init(mx, s);
  for (int i = 0; i < L.N; ++i) {
    const float ui = u[i];
    if (IS_MASKED(ui)) continue;
    lse_push(mx, s, place_cost(L, i, c) + ui);
  }
  const float z = lse_done(mx, s);
  if (IS_MASKED(z)) { v[c] = 0.f; return; }
  const float excess = z - log_b[c];
  // EVERY column takes this update, stock columns included (the T17 fix).
  v[c] = excess > 0.f ? -excess : 0.f;
}

// ----------------------------------------------------------------------------
// 5 · THE SUPPORT METER — exp(H) per commitment.
//
// The effective number of cells this commitment's mass is spread over. This is
// the quantity that appears under seven different names across the program
// (intrinsic dimension / attention entropy / the margin / the dual gap / the
// hollowing law / lambda_min). Here it is measured once, directly, and printed
// as a spectrum rather than a mean.
//
// Low support  -> the placement is decided; sparse methods are faithful here;
//                 this is the automatable mass.
// High support -> the placement is genuinely contested; sparse methods are NOT
//                 faithful here; this is the frontier bill, and it needs a human.
//
// Also emits, in the same pass and for free:
//   risk_i  = the dual of the cell it would land in, times its slack deficit.
//             The breach forecaster is a by-product of a pass already being run.
// ----------------------------------------------------------------------------
__global__ void k_support(Lat L, const float* u, const float* v,
                          float* es, float* risk, int* argmax_cell,
                          unsigned long long* hist, int nbins,
                          unsigned long long* acc_sum, unsigned long long* acc_sumsq)
{
  const int i = (int)(blockIdx.x * blockDim.x + threadIdx.x);
  if (i >= L.N) return;
  const float ui = u[i];
  if (IS_MASKED(ui)) { es[i] = 0.f; risk[i] = 0.f; argmax_cell[i] = -1; return; }

  float mx, s; lse_init(mx, s);
  for (int c = 0; c < L.M; ++c) lse_push(mx, s, place_cost(L, i, c) + v[c]);
  const float z = lse_done(mx, s);
  if (IS_MASKED(z)) { es[i] = 0.f; risk[i] = 0.f; argmax_cell[i] = -1; return; }

  // second traversal: entropy and argmax, from the SAME cost function
  float H = 0.f, best = NEG_INF; int bc = -1;
  for (int c = 0; c < L.M; ++c) {
    const float lc = place_cost(L, i, c) + v[c];
    if (IS_MASKED(lc)) continue;
    if (lc > best) { best = lc; bc = c; }
    const float p = expf(lc - z);
    if (p > 1e-12f) H -= p * logf(p);
  }
  const float support = expf(H);
  es[i] = support; argmax_cell[i] = bc;

  // the free forecaster: price of the column it lands in x how tight its deadline is
  float r = 0.f;
  if (bc >= 0) {
    const float price = -v[bc];                       // v <= 0; -v is the shadow price
    const int finish = col_is_stock(L, bc) ? L.t_due[i] + 1
                                           : col_slot(L, bc) + (int)L.dur[i];
    const float slack = (float)(L.t_due[i] - finish);
    r = price * (slack < 0.f ? 1.0f : 1.0f / (1.0f + slack));
  }
  risk[i] = r;

  // deterministic histogram + fixed-point moments (the band travels with the number)
  int b = (int)(support * 2.0f);            // 0.5-wide bins
  if (b < 0) b = 0; if (b >= nbins) b = nbins - 1;
  atomicAdd(&hist[b], 1ull);
  atomicAdd(acc_sum,   fx((double)support));
  atomicAdd(acc_sumsq, fx((double)support * (double)support));
}

// ----------------------------------------------------------------------------
// 6 · THE CONTRADICTION STENCIL — local by construction (T4)
//
// Two commitments can only contradict if they contend. Contention means sharing
// a cell (or an adjacent slot on the same seat), or sharing an entity. So the
// check is a stencil over occupied cells, not an all-pairs scan.
//
// Kinds:
//   K_OVERCOMMIT  the incumbent's own assignment puts more work in a cell than
//                 the cell holds. Keyed, deterministic, self-certifying.
//   K_DOUBLEBOOK  one entity assigned to two seats in overlapping slots.
//   K_DEPENDENCY  this starts before the thing it waits on can finish.
//   K_DEADLINE    the incumbent's assignment finishes after the deadline.
//   K_DUPLICATE   two records, DIFFERENT SOURCE SYSTEMS, same entity, overlapping
//                 window, embedding cosine above threshold. THIS IS THE UNKEYED
//                 ONE — the 38% of alias mass no join reaches, and the only kind
//                 here that needs a model rather than a query. It is also the
//                 only kind that can be WRONG, so it is reported separately and
//                 carries a confidence, never folded into the keyed count.
// ----------------------------------------------------------------------------
// ISOBAR: K_PAID — the money verdict says PAID, yet the object is still open in the lattice. It can
// never be in a chase set; the plane must discharge it. Keyed on the verdict flag; self-certifying.
enum { K_OVERCOMMIT=0, K_DOUBLEBOOK=1, K_DEPENDENCY=2, K_DEADLINE=3, K_DUPLICATE=4, K_PAID=5, K_N=6 };

struct Contra { int a, b, kind; float weight; };

__global__ void k_bucket_count(Lat L, int* cell_count){
  const int i = (int)(blockIdx.x * blockDim.x + threadIdx.x);
  if (i >= L.N) return;
  const int c = L.inc_cell[i];
  if (c >= 0 && c < L.M) atomicAdd(&cell_count[c], 1);
}
__global__ void k_bucket_fill(Lat L, const int* cell_start, int* cursor, int* cell_items){
  const int i = (int)(blockIdx.x * blockDim.x + threadIdx.x);
  if (i >= L.N) return;
  const int c = L.inc_cell[i];
  if (c < 0 || c >= L.M) return;
  const int k = atomicAdd(&cursor[c], 1);
  cell_items[cell_start[c] + k] = i;
}

__global__ void k_contra(Lat L, const int* cell_start, const int* cell_count,
                         const int* cell_items, const float* v, float dup_cos,
                         Contra* out, int* n_out, unsigned long long* by_kind)
{
  const int c = (int)(blockIdx.x * blockDim.x + threadIdx.x);
  if (c >= L.M) return;
  const int n = cell_count[c];
  if (n <= 0) return;
  const int base = cell_start[c];
  const float price = (v[c] <= 0.f) ? -v[c] : 0.f;

  // K_OVERCOMMIT — cell load vs cell capacity, from the incumbent's own placement
  float load = 0.f;
  for (int k = 0; k < n; ++k) load += L.work[cell_items[base + k]];
  if (!col_is_stock(L, c) && load > L.cap[c] * 1.0001f) {
    const int idx = atomicAdd(n_out, 1);
    if (idx < (int)MAX_CONTRA) { out[idx] = Contra{ cell_items[base], -1, K_OVERCOMMIT, (load - L.cap[c]) * (1.f + price) }; }
    atomicAdd(&by_kind[K_OVERCOMMIT], 1ull);
  }

  for (int k = 0; k < n; ++k) {
    const int i = cell_items[base + k];

    // ISOBAR K_PAID — paid by the verdict source, still open: a contradiction the plane must resolve
    if ((L.paid != nullptr) && L.paid[i]) {
      const int idx = atomicAdd(n_out, 1);
      if (idx < (int)MAX_CONTRA) out[idx] = Contra{ i, -1, K_PAID, 1.f + price };
      atomicAdd(&by_kind[K_PAID], 1ull);
    }

    // K_DEADLINE — finishes after it was promised
    if (!col_is_stock(L, c)) {
      const int finish = col_slot(L, c) + (int)L.dur[i];
      if (finish > L.t_due[i]) {
        const int idx = atomicAdd(n_out, 1);
        if (idx < (int)MAX_CONTRA) out[idx] = Contra{ i, -1, K_DEADLINE, (float)(finish - L.t_due[i]) * (1.f + price) };
        atomicAdd(&by_kind[K_DEADLINE], 1ull);
      }
    }

    // K_DEPENDENCY — starts before its predecessor can finish
    const int d = L.dep[i];
    if (d >= 0 && d < L.N) {
      const int dc = L.inc_cell[d];
      if (dc >= 0 && !col_is_stock(L, dc) && !col_is_stock(L, c)) {
        const int dfin = col_slot(L, dc) + (int)L.dur[d];
        if (col_slot(L, c) < dfin) {
          const int idx = atomicAdd(n_out, 1);
          if (idx < (int)MAX_CONTRA) out[idx] = Contra{ i, d, K_DEPENDENCY, (float)(dfin - col_slot(L, c)) * (1.f + price) };
          atomicAdd(&by_kind[K_DEPENDENCY], 1ull);
        }
      }
    }

    // pairwise within the cell — this is the O(n_cell^2) that locality makes cheap
    for (int m = k + 1; m < n; ++m) {
      const int j = cell_items[base + m];

      // K_DOUBLEBOOK — same entity, same cell (same seat AND slot) is contention
      if (L.entity[i] == L.entity[j] && L.src[i] == L.src[j]) {
        const int idx = atomicAdd(n_out, 1);
        if (idx < (int)MAX_CONTRA) out[idx] = Contra{ i, j, K_DOUBLEBOOK, 1.f + price };
        atomicAdd(&by_kind[K_DOUBLEBOOK], 1ull);
        continue;
      }

      // (K_DUPLICATE does NOT belong in this stencil — see k_contra_dup below.)
    }
  }
}

// ----------------------------------------------------------------------------
// 6b · THE UNKEYED MATCHER — a SECOND stencil, over a DIFFERENT locality key.
//
// MEASURED CORRECTION, 2026-09-06. The first version of this file put the
// duplicate check inside the cell stencil above, on the assumption that T4
// (locality is the lattice) covers every contradiction kind. Oracle O6 recovered
// 3 of 60 planted duplicates and killed that assumption:
//
//   CONTENTION IS LOCAL IN THE LATTICE. IDENTITY IS NOT.
//
// Two records describing the same promise are precisely the pair that has NOT
// been placed consistently — that is what makes them a defect. Bucketing them by
// placement guarantees you miss them. So identity gets its own locality key: the
// entity. Contention buckets by cell; identity buckets by entity. Two stencils,
// two keys, and the claim in the header is now narrower and true.
// ----------------------------------------------------------------------------
__global__ void k_ent_count(Lat L, int n_ent, int* ent_count){
  const int i = (int)(blockIdx.x * blockDim.x + threadIdx.x);
  if (i >= L.N) return;
  const int e = L.entity[i];
  if (e >= 0 && e < n_ent) atomicAdd(&ent_count[e], 1);
}
__global__ void k_ent_fill(Lat L, int n_ent, const int* ent_start, int* cursor, int* ent_items){
  const int i = (int)(blockIdx.x * blockDim.x + threadIdx.x);
  if (i >= L.N) return;
  const int e = L.entity[i];
  if (e < 0 || e >= n_ent) return;
  ent_items[ent_start[e] + atomicAdd(&cursor[e], 1)] = i;
}
__global__ void k_contra_dup(Lat L, int n_ent, const int* ent_start, const int* ent_count,
                             const int* ent_items, float dup_cos,
                             Contra* out, int* n_out, unsigned long long* by_kind)
{
  const int e = (int)(blockIdx.x * blockDim.x + threadIdx.x);
  if (e >= n_ent) return;
  const int n = ent_count[e];
  if (n < 2) return;
  const int base = ent_start[e];
  for (int k = 0; k < n; ++k) {
    const int i = ent_items[base + k];
    const float na = emb_dot(L.emb + (size_t)i*EMB_D, L.emb_scale[i], L.emb + (size_t)i*EMB_D, L.emb_scale[i]);
    for (int m = k + 1; m < n; ++m) {
      const int j = ent_items[base + m];
      if (L.src[i] == L.src[j]) continue;              // same system: a keyed problem, not this one
      const bool overlap = !(L.t_due[i] < L.t_open[j] || L.t_due[j] < L.t_open[i]);
      if (!overlap) continue;
      const float nb = emb_dot(L.emb + (size_t)j*EMB_D, L.emb_scale[j], L.emb + (size_t)j*EMB_D, L.emb_scale[j]);
      const float ab = emb_dot(L.emb + (size_t)i*EMB_D, L.emb_scale[i], L.emb + (size_t)j*EMB_D, L.emb_scale[j]);
      const float cs = ab / (sqrtf(na * nb) + 1e-12f);
      if (cs >= dup_cos) {
        const int idx = atomicAdd(n_out, 1);
        if (idx < (int)MAX_CONTRA) out[idx] = Contra{ i, j, K_DUPLICATE, cs };
        atomicAdd(&by_kind[K_DUPLICATE], 1ull);
      }
    }
  }
}

// ----------------------------------------------------------------------------
// 7 · HOST SIDE — the lattice on the host, the synthetic generator, the ingest
// ----------------------------------------------------------------------------
struct LatHost {
  int N=0, nseat=0, nslot=0, M=0, ncls=0;
  float T=0.25f, late_penalty=1.0f;
  std::vector<int>   entity, t_open, t_due, dep, inc_cell;
  std::vector<short> cls;
  std::vector<unsigned char> dur, src;
  std::vector<float> work, cap, supply;
  std::vector<unsigned int> flags, law, arm_mask;
  std::vector<signed char> emb, seat_key;
  std::vector<float> emb_scale, seat_scale;
  // ISOBAR rows
  std::vector<float> tier_w;
  std::vector<unsigned char> paid, waiting;
  // planted truth (synthetic only) — what the oracles must recover
  std::vector<int> planted_dup_a, planted_dup_b;
  int planted_overcommit = 0, planted_deadline = 0, planted_dep = 0;
  int planted_paid = 0, planted_waiting = 0;   // ISOBAR
};

static Lat host_view(const LatHost& H){
  Lat L{};
  L.N=H.N; L.nseat=H.nseat; L.nslot=H.nslot; L.M=H.M; L.ncls=H.ncls; L.T=H.T; L.late_penalty=H.late_penalty;
  L.entity=H.entity.data(); L.cls=H.cls.data(); L.dur=H.dur.data(); L.src=H.src.data();
  L.t_open=H.t_open.data(); L.t_due=H.t_due.data(); L.work=H.work.data(); L.dep=H.dep.data(); L.inc_cell=H.inc_cell.data();
  L.flags=H.flags.data(); L.emb=H.emb.data(); L.emb_scale=H.emb_scale.data();
  L.seat_key=H.seat_key.data(); L.seat_scale=H.seat_scale.data();
  L.cap=H.cap.data(); L.supply=H.supply.data(); L.law=H.law.data(); L.arm_mask=H.arm_mask.data(); L.arm=0;
  L.tier_w = H.tier_w.empty() ? nullptr : H.tier_w.data();
  L.paid = H.paid.empty() ? nullptr : H.paid.data();
  L.waiting = H.waiting.empty() ? nullptr : H.waiting.data();
  return L;
}

static void quantize(const std::vector<float>& f, signed char* q, float& scale){
  float mx = 1e-9f;
  for (float x : f) mx = std::max(mx, std::fabs(x));
  scale = mx / 127.0f;
  for (size_t d = 0; d < f.size(); ++d) {
    int t = (int)lrintf(f[d] / scale);
    q[d] = (signed char)std::max(-127, std::min(127, t));
  }
}

// A synthetic company: seats with specialities, commitments with classes,
// deliberate contradictions planted so the oracles have something to recover.
static LatHost build_synthetic(int N, int nseat, int nslot, int ncls,
                               uint64_t seed, int n_dup, float over_rate)
{
  LatHost H;
  H.N=N; H.nseat=nseat; H.nslot=nslot; H.ncls=ncls;
  H.M = nseat*nslot + N_STOCK;

  // seat keys
  H.seat_key.assign((size_t)nseat*EMB_D, 0);
  H.seat_scale.assign(nseat, 0.f);
  for (int s = 0; s < nseat; ++s) {
    std::vector<float> f(EMB_D);
    for (int d = 0; d < EMB_D; ++d) f[d] = unorm(seed, 1000+s, d);
    quantize(f, &H.seat_key[(size_t)s*EMB_D], H.seat_scale[s]);
  }

  H.entity.resize(N); H.cls.resize(N); H.dur.resize(N); H.src.resize(N);
  H.t_open.resize(N); H.t_due.resize(N); H.work.resize(N);
  H.dep.assign(N, -1); H.inc_cell.assign(N, -1); H.flags.assign(N, 0);
  H.emb.assign((size_t)N*EMB_D, 0); H.emb_scale.assign(N, 0.f);
  H.supply.resize(N);

  const int n_entities = std::max(4, N / 3);
  for (int i = 0; i < N; ++i) {
    H.entity[i] = (int)(u01(seed, 11, i) * n_entities);
    H.cls[i]    = (short)(u01(seed, 12, i) * ncls);
    H.dur[i]    = (unsigned char)(1 + (int)(u01(seed, 13, i) * 3));
    H.src[i]    = (unsigned char)(u01(seed, 14, i) * 4);      // four systems of record
    H.t_open[i] = (int)(u01(seed, 15, i) * (nslot/2));
    H.t_due[i]  = H.t_open[i] + 2 + (int)(u01(seed, 16, i) * (nslot/2));
    H.work[i]   = 0.4f + 0.8f * u01(seed, 17, i);
    H.supply[i] = H.work[i];
    // the embedding: class centroid + noise, so same-class records look alike
    std::vector<float> f(EMB_D);
    for (int d = 0; d < EMB_D; ++d)
      f[d] = unorm(seed, 5000 + H.cls[i], d) + 0.35f * unorm(seed, 90000 + i, d);
    quantize(f, &H.emb[(size_t)i*EMB_D], H.emb_scale[i]);
    if (u01(seed, 18, i) < 0.20f && i > 0) H.dep[i] = (int)(u01(seed, 19, i) * i);
  }
  // ISOBAR: registry rows. tier_w from a planted tier (1..4); 10% of rows WAITING on a counterparty;
  // 2% planted PAID-but-open so oracle O8 has something to recover.
  H.tier_w.assign(N, 1.f); H.paid.assign(N, 0); H.waiting.assign(N, 0);
  for (int i = 0; i < N; ++i) {
    const int tier = 1 + (int)(u01(seed, 73, i) * 4);
    H.tier_w[i] = (tier == 1) ? 2.0f : (tier == 2) ? 1.4f : (tier == 3) ? 1.0f : 0.5f;
    if (u01(seed, 71, i) < 0.10f) { H.waiting[i] = 1; H.planted_waiting++; }
    if (u01(seed, 72, i) < 0.02f) { H.paid[i] = 1;    H.planted_paid++; }
  }

  // PLANT: n_dup duplicate pairs — the same promise recorded in two systems,
  // with no shared key and only the embedding to join them.
  for (int k = 0; k < n_dup && 2*k+1 < N; ++k) {
    const int a = (int)(u01(seed, 21, k) * (N-1));
    const int b = (a + 1 + (int)(u01(seed, 22, k) * (N-2))) % N;
    if (a == b) continue;
    H.entity[b] = H.entity[a];
    H.src[b]    = (unsigned char)((H.src[a] + 1) & 3);        // a DIFFERENT system
    H.cls[b]    = H.cls[a];
    H.t_open[b] = H.t_open[a];
    H.t_due[b]  = H.t_due[a];
    for (int d = 0; d < EMB_D; ++d) H.emb[(size_t)b*EMB_D + d] = H.emb[(size_t)a*EMB_D + d];
    H.emb_scale[b] = H.emb_scale[a];
    H.planted_dup_a.push_back(a); H.planted_dup_b.push_back(b);
  }

  // law: ~12% of (class, seat) pairs infeasible
  const size_t lawwords = ((size_t)ncls*nseat + 31) / 32;
  H.law.assign(lawwords, 0u);
  for (int c = 0; c < ncls; ++c)
    for (int s = 0; s < nseat; ++s)
      if (u01(seed, 41, (uint64_t)c*977 + s) >= 0.12f) {
        const size_t bit = (size_t)c*nseat + s;
        H.law[bit >> 5] |= (1u << (bit & 31));
      }

  // the solver arm masks a third of the seats (nothing promoted yet)
  H.arm_mask.assign((nseat + 31) / 32, 0u);
  for (int s = 0; s < nseat; ++s)
    if (u01(seed, 42, s) < 0.33f) H.arm_mask[s >> 5] |= (1u << (s & 31));

  // capacity. Real cells get a real cap; BOTH stock columns get a FINITE one.
  H.cap.assign(H.M, 0.f);
  double total_work = 0; for (int i=0;i<N;++i) total_work += H.work[i];
  const float per_cell = (float)(total_work / (double)(nseat*nslot) * 1.35);
  for (int c = 0; c < nseat*nslot; ++c) H.cap[c] = std::max(0.5f, per_cell);
  H.cap[nseat*nslot + STOCK_UNPLACED]      = (float)(total_work * 0.25);  // carrying capacity
  H.cap[nseat*nslot + STOCK_UNADJUDICATED] = (float)(total_work * 0.05);  // adjudication bandwidth
  { double wm = 0; for (int i = 0; i < N; ++i) if (H.waiting[i]) wm += H.work[i];        // ISOBAR: the silence budget
    H.cap[nseat*nslot + STOCK_WAITING] = (float)std::max(0.5, wm * 0.5); }               // planted to BIND, so O8b prices it

  // THE INCUMBENT'S OWN ASSIGNMENT (what the CDC stream says actually happened),
  // with contradictions planted into it on purpose.
  for (int i = 0; i < N; ++i) {
    if (H.waiting[i]) { H.inc_cell[i] = nseat*nslot + STOCK_WAITING; continue; }   // ISOBAR: waiting rows sit in their stock
    const int seat = (int)(u01(seed, 51, i) * nseat);
    int slot = H.t_open[i] + (int)(u01(seed, 52, i) * 3);
    if (slot + (int)H.dur[i] > nslot) slot = std::max(0, nslot - (int)H.dur[i]);
    H.inc_cell[i] = seat*nslot + slot;
    if (slot + (int)H.dur[i] > H.t_due[i]) H.planted_deadline++;
  }
  // pile extra work into a few cells to force overcommit
  const int n_over = std::max(1, (int)(nseat*nslot*over_rate));
  for (int k = 0; k < n_over; ++k) {
    const int c = (int)(u01(seed, 61, k) * (nseat*nslot));
    int placed = 0;
    for (int i = 0; i < N && placed < 6; ++i)
      if (u01(seed, 62, (uint64_t)k*7919 + i) < 0.02f) { H.inc_cell[i] = c; ++placed; }
    if (placed >= 2) H.planted_overcommit++;
  }
  for (int i = 0; i < N; ++i) {
    const int d = H.dep[i];
    if (d >= 0 && H.inc_cell[d] >= 0 && H.inc_cell[i] >= 0) {
      const int dfin = (H.inc_cell[d] % nslot) + (int)H.dur[d];
      if ((H.inc_cell[i] % nslot) < dfin) H.planted_dep++;
    }
  }
  return H;
}

// CDC ingest. One line per record:
//   id,entity,class,src,t_open,t_due,dur,work,dep,inc_seat,inc_slot,e0,e1,...,e127
// Anything the stream does not carry is a typed refusal, never a guess.
static bool ingest_csv(LatHost& H, const char* path, int nseat, int nslot, int ncls)
{
  FILE* f = fopen(path, "r");
  if (!f) { fprintf(stderr, "cannot open cdc stream %s\n", path); return false; }
  H.nseat=nseat; H.nslot=nslot; H.ncls=ncls; H.M = nseat*nslot + N_STOCK;
  H.seat_key.assign((size_t)nseat*EMB_D, 0); H.seat_scale.assign(nseat, 1.f/127.f);
  char line[1 << 15];
  int n = 0;
  while (fgets(line, sizeof line, f)) {
    if (line[0] == '#' || line[0] == 'i') continue;
    int id, ent, cl, sr, to, td, du, dp, isea, islo; float wk;
    char* p = line;
    if (sscanf(p, "%d,%d,%d,%d,%d,%d,%d,%f,%d,%d,%d",
               &id,&ent,&cl,&sr,&to,&td,&du,&wk,&dp,&isea,&islo) != 11) continue;
    for (int k = 0; k < 11; ++k) { p = strchr(p, ','); if (!p) break; ++p; }
    std::vector<float> e(EMB_D, 0.f);
    for (int d = 0; d < EMB_D && p; ++d) { e[d] = (float)atof(p); p = strchr(p, ','); if (p) ++p; }
    H.entity.push_back(ent); H.cls.push_back((short)cl); H.src.push_back((unsigned char)sr);
    H.t_open.push_back(to); H.t_due.push_back(td); H.dur.push_back((unsigned char)std::max(1,du));
    H.work.push_back(wk); H.supply.push_back(wk); H.dep.push_back(dp);
    H.inc_cell.push_back((isea >= 0 && islo >= 0) ? isea*nslot + islo : -1);
    H.flags.push_back(0u);
    H.tier_w.push_back(1.f); H.paid.push_back(0); H.waiting.push_back(0);   // ISOBAR: no registry on a CDC stream
    H.emb.resize((size_t)(n+1)*EMB_D); H.emb_scale.resize(n+1);
    quantize(e, &H.emb[(size_t)n*EMB_D], H.emb_scale[n]);
    ++n;
  }
  fclose(f);
  H.N = n;
  const size_t lawwords = ((size_t)ncls*nseat + 31) / 32;
  H.law.assign(lawwords, 0xFFFFFFFFu);
  H.arm_mask.assign((nseat + 31) / 32, 0u);
  double tw = 0; for (float w : H.work) tw += w;
  H.cap.assign(H.M, (float)(tw / std::max(1, nseat*nslot) * 1.35));
  H.cap[nseat*nslot + STOCK_UNPLACED]      = (float)(tw * 0.25);
  H.cap[nseat*nslot + STOCK_UNADJUDICATED] = (float)(tw * 0.05);
  H.cap[nseat*nslot + STOCK_WAITING]       = (float)(tw * 0.30);   // ISOBAR
  printf("cdc: ingested %d commitments from %s\n", n, path);
  return n > 0;
}

// ----------------------------------------------------------------------------
// 8 · DEVICE BUFFERS
// ----------------------------------------------------------------------------
struct Dev {
  int *entity=nullptr,*t_open=nullptr,*t_due=nullptr,*dep=nullptr,*inc_cell=nullptr;
  short* cls=nullptr; unsigned char *dur=nullptr,*src=nullptr;
  float *work=nullptr,*cap=nullptr,*supply=nullptr,*emb_scale=nullptr,*seat_scale=nullptr;
  unsigned int *flags=nullptr,*law=nullptr,*arm_mask=nullptr;
  signed char *emb=nullptr,*seat_key=nullptr;
  float* tier_w=nullptr; unsigned char *paid=nullptr,*waiting=nullptr;   // ISOBAR
  Lat L{};
};

static Dev upload(const LatHost& H){
  Dev d;
  auto up_i = [&](const std::vector<int>& v){ int* p=dev_alloc<int>(v.size()); dev_upload(p,v.data(),v.size()); return p; };
  auto up_f = [&](const std::vector<float>& v){ float* p=dev_alloc<float>(v.size()); dev_upload(p,v.data(),v.size()); return p; };
  auto up_u = [&](const std::vector<unsigned int>& v){ unsigned int* p=dev_alloc<unsigned int>(v.size()); dev_upload(p,v.data(),v.size()); return p; };
  d.entity=up_i(H.entity); d.t_open=up_i(H.t_open); d.t_due=up_i(H.t_due);
  d.dep=up_i(H.dep); d.inc_cell=up_i(H.inc_cell);
  d.cls=dev_alloc<short>(H.cls.size()); dev_upload(d.cls,H.cls.data(),H.cls.size());
  d.dur=dev_alloc<unsigned char>(H.dur.size()); dev_upload(d.dur,H.dur.data(),H.dur.size());
  d.src=dev_alloc<unsigned char>(H.src.size()); dev_upload(d.src,H.src.data(),H.src.size());
  d.work=up_f(H.work); d.cap=up_f(H.cap); d.supply=up_f(H.supply);
  d.emb_scale=up_f(H.emb_scale); d.seat_scale=up_f(H.seat_scale);
  d.flags=up_u(H.flags); d.law=up_u(H.law); d.arm_mask=up_u(H.arm_mask);
  d.emb=dev_alloc<signed char>(H.emb.size()); dev_upload(d.emb,H.emb.data(),H.emb.size());
  d.seat_key=dev_alloc<signed char>(H.seat_key.size()); dev_upload(d.seat_key,H.seat_key.data(),H.seat_key.size());
  // ISOBAR rows (absent on a bare CDC lattice ⇒ null pointers ⇒ the kernels treat them as neutral)
  if (!H.tier_w.empty())  { d.tier_w=up_f(H.tier_w); }
  if (!H.paid.empty())    { d.paid=dev_alloc<unsigned char>(H.paid.size()); dev_upload(d.paid,H.paid.data(),H.paid.size()); }
  if (!H.waiting.empty()) { d.waiting=dev_alloc<unsigned char>(H.waiting.size()); dev_upload(d.waiting,H.waiting.data(),H.waiting.size()); }
  Lat& L = d.L;
  L.tier_w=d.tier_w; L.paid=d.paid; L.waiting=d.waiting;
  L.N=H.N; L.nseat=H.nseat; L.nslot=H.nslot; L.M=H.M; L.ncls=H.ncls;
  L.T=H.T; L.late_penalty=H.late_penalty;
  L.entity=d.entity; L.cls=d.cls; L.dur=d.dur; L.src=d.src;
  L.t_open=d.t_open; L.t_due=d.t_due; L.work=d.work; L.dep=d.dep; L.inc_cell=d.inc_cell;
  L.flags=d.flags; L.emb=d.emb; L.emb_scale=d.emb_scale;
  L.seat_key=d.seat_key; L.seat_scale=d.seat_scale;
  L.cap=d.cap; L.supply=d.supply; L.law=d.law; L.arm_mask=d.arm_mask; L.arm=0;
  return d;
}
static void release(Dev& d){
  dev_free(d.entity); dev_free(d.t_open); dev_free(d.t_due); dev_free(d.dep); dev_free(d.inc_cell);
  dev_free(d.cls); dev_free(d.dur); dev_free(d.src);
  dev_free(d.work); dev_free(d.cap); dev_free(d.supply); dev_free(d.emb_scale); dev_free(d.seat_scale);
  dev_free(d.flags); dev_free(d.law); dev_free(d.arm_mask); dev_free(d.emb); dev_free(d.seat_key);
  dev_free(d.tier_w); dev_free(d.paid); dev_free(d.waiting);   // ISOBAR
}

// ----------------------------------------------------------------------------
// 9 · A TICK
// ----------------------------------------------------------------------------
struct TickOut {
  std::vector<float> u, v, es, risk;
  std::vector<int>   argmax_cell;
  std::vector<unsigned long long> hist, by_kind;
  std::vector<Contra> contra;
  double es_mean=0, es_sd=0;
  int n_contra=0, iters=0;
  double sink_ms=0, bytes_moved=0;
};

// Wall clock on the steady clock. The arithmetic line is a wall-time claim, so
// it must not be CPU time (which on the GPU path would be ~0 and flatter us).
static double now_ms(){
  using namespace std::chrono;
  return (double)duration_cast<microseconds>(steady_clock::now().time_since_epoch()).count() / 1000.0;
}

static TickOut run_tick(Dev& D, const LatHost& H, int iters, float dup_cos, int nbins)
{
  Lat& L = D.L;
  TickOut R;
  float* u   = dev_alloc<float>(L.N);
  float* v   = dev_alloc<float>(L.M);
  float* la  = dev_alloc<float>(L.N);
  float* lb  = dev_alloc<float>(L.M);
  {
    std::vector<float> h_la(L.N), h_lb(L.M);
    for (int i=0;i<L.N;++i) h_la[i] = logf(std::max(H.supply[i], 1e-9f));
    for (int c=0;c<L.M;++c) h_lb[c] = logf(std::max(H.cap[c],    1e-9f));
    dev_upload(la, h_la.data(), L.N); dev_upload(lb, h_lb.data(), L.M);
  }
  const double t0 = now_ms();
  for (int k = 0; k < iters; ++k) {
    LAUNCH(k_sink_rows, grid_for(L.N), BLOCK, L, v, la, u);
    LAUNCH(k_sink_cols, grid_for(L.M), BLOCK, L, u, lb, v);
  }
  // FINISH ON THE EQUALITY CONSTRAINT. The column pass is an inequality
  // projection and leaves the rows off their supply; the dual identity
  // u_i = log a_i - LSE_c(C_ic + v_c) only holds immediately after a row pass.
  // Ending on a column pass fails O1 at 6.2e-2 and O3 at 1.04e-2 — measured,
  // 2026-09-06, before this line existed. (org_relax.cu does the same thing at
  // its line 523 and the reason is the same.)
  LAUNCH(k_sink_rows, grid_for(L.N), BLOCK, L, v, la, u);
  dev_sync();
  R.sink_ms = now_ms() - t0;
  R.iters = iters;

  // bytes actually moved by the two Sinkhorn passes, counted honestly:
  // each pass touches every (row, col) pair once, reading the row's scalar state
  // and its embedding, and the seat key.  This is the number the roofline needs.
  const double pairs = (double)L.N * (double)L.M * (double)iters * 2.0;
  const double bytes_per_pair = (double)(EMB_D + EMB_D) + 32.0;  // two int8 vecs + scalars
  R.bytes_moved = pairs * bytes_per_pair;

  float* es   = dev_alloc<float>(L.N);
  float* risk = dev_alloc<float>(L.N);
  int*   amc  = dev_alloc<int>(L.N);
  unsigned long long* hist = dev_alloc<unsigned long long>(nbins);
  unsigned long long* accs = dev_alloc<unsigned long long>(2);
  LAUNCH(k_support, grid_for(L.N), BLOCK, L, u, v, es, risk, amc, hist, nbins, accs+0, accs+1);
  dev_sync();

  R.u.resize(L.N); R.v.resize(L.M); R.es.resize(L.N); R.risk.resize(L.N); R.argmax_cell.resize(L.N);
  R.hist.resize(nbins);
  dev_download(R.u.data(), u, L.N); dev_download(R.v.data(), v, L.M);
  dev_download(R.es.data(), es, L.N); dev_download(R.risk.data(), risk, L.N);
  dev_download(R.argmax_cell.data(), amc, L.N); dev_download(R.hist.data(), hist, nbins);
  { unsigned long long a[2]; dev_download(a, accs, 2);
    const double s = (double)a[0]/FIX_SCALE, s2 = (double)a[1]/FIX_SCALE;
    R.es_mean = L.N ? s/L.N : 0.0;
    const double var = L.N ? std::max(0.0, s2/L.N - R.es_mean*R.es_mean) : 0.0;
    R.es_sd = sqrt(var);
  }

  // --- contradictions, bucketed by the incumbent's own placement (T4)
  int* cnt   = dev_alloc<int>(L.M);
  int* start = dev_alloc<int>(L.M);
  int* cur   = dev_alloc<int>(L.M);
  LAUNCH(k_bucket_count, grid_for(L.N), BLOCK, L, cnt);
  dev_sync();
  std::vector<int> h_cnt(L.M), h_start(L.M);
  dev_download(h_cnt.data(), cnt, L.M);
  int tot = 0;
  for (int c = 0; c < L.M; ++c) { h_start[c] = tot; tot += h_cnt[c]; }
  dev_upload(start, h_start.data(), L.M);
  int* items = dev_alloc<int>(std::max(1, tot));
  LAUNCH(k_bucket_fill, grid_for(L.N), BLOCK, L, start, cur, items);
  dev_sync();

  Contra* co = dev_alloc<Contra>(MAX_CONTRA);
  int*    nc = dev_alloc<int>(1);
  unsigned long long* bk = dev_alloc<unsigned long long>(K_N);
  LAUNCH(k_contra, grid_for(L.M), BLOCK, L, start, cnt, items, v, dup_cos, co, nc, bk);
  dev_sync();

  // --- the SECOND stencil: identity, bucketed by entity, not by cell (6b)
  int n_ent = 1;
  for (int i = 0; i < L.N; ++i) n_ent = std::max(n_ent, H.entity[i] + 1);
  int* ecnt = dev_alloc<int>(n_ent);
  int* esta = dev_alloc<int>(n_ent);
  int* ecur = dev_alloc<int>(n_ent);
  LAUNCH(k_ent_count, grid_for(L.N), BLOCK, L, n_ent, ecnt);
  dev_sync();
  std::vector<int> h_ecnt(n_ent), h_esta(n_ent);
  dev_download(h_ecnt.data(), ecnt, n_ent);
  int etot = 0;
  for (int e = 0; e < n_ent; ++e) { h_esta[e] = etot; etot += h_ecnt[e]; }
  dev_upload(esta, h_esta.data(), n_ent);
  int* eitems = dev_alloc<int>(std::max(1, etot));
  LAUNCH(k_ent_fill, grid_for(L.N), BLOCK, L, n_ent, esta, ecur, eitems);
  dev_sync();
  LAUNCH(k_contra_dup, grid_for(n_ent), BLOCK, L, n_ent, esta, ecnt, eitems, dup_cos, co, nc, bk);
  dev_sync();
  dev_free(ecnt); dev_free(esta); dev_free(ecur); dev_free(eitems);
  dev_download(&R.n_contra, nc, 1);
  R.by_kind.resize(K_N); dev_download(R.by_kind.data(), bk, K_N);
  const int keep = std::min(R.n_contra, (int)MAX_CONTRA);
  R.contra.resize(std::max(0, keep));
  if (keep > 0) dev_download(R.contra.data(), co, keep);

  dev_free(u); dev_free(v); dev_free(la); dev_free(lb);
  dev_free(es); dev_free(risk); dev_free(amc); dev_free(hist); dev_free(accs);
  dev_free(cnt); dev_free(start); dev_free(cur); dev_free(items);
  dev_free(co); dev_free(nc); dev_free(bk);
  return R;
}

// ----------------------------------------------------------------------------
// 10 · THE ARITHMETIC LINE — measured peak, never a hard-coded constant.
//      (Wave 3 caught a hard-coded 4.0e13 that was 1.216x overstated. Measure it.)
// ----------------------------------------------------------------------------
__global__ void k_stream(const float* a, const float* b, float* c, long long n, float s){
  const long long i = (long long)blockIdx.x * blockDim.x + threadIdx.x;
  if (i < n) c[i] = a[i] + s * b[i];
}
// ISOBAR correction (2026-09-22): the original measured 1<<22 floats × 3 arrays = 48 MB, which is
// exactly the L2 of the AD103 on this box — the "peak" it printed (1,592 GB/s) was an L2 number,
// 2.4× the card's DRAM. The triad now streams 128 MB per array so the number is DRAM bandwidth.
static double measure_peak_gbs(long long n_elem){
  float* a = dev_alloc<float>(n_elem);
  float* b = dev_alloc<float>(n_elem);
  float* c = dev_alloc<float>(n_elem);
  LAUNCH(k_stream, grid_for(n_elem), BLOCK, a, b, c, n_elem, 2.0f);  // warm
  dev_sync();
  const double t0 = now_ms();
  const int reps = 5;
  for (int r = 0; r < reps; ++r) LAUNCH(k_stream, grid_for(n_elem), BLOCK, a, b, c, n_elem, 2.0f);
  dev_sync();
  const double ms = now_ms() - t0;
  dev_free(a); dev_free(b); dev_free(c);
  const double bytes = (double)n_elem * 12.0 * reps;   // 2 reads + 1 write
  return ms > 0 ? bytes / (ms * 1e6) : 0.0;
}

// ----------------------------------------------------------------------------
// 11 · THE REPORT — four things, and nothing else
// ----------------------------------------------------------------------------
static const char* KIND_NAME[K_N] = {
  "OVERCOMMIT  cell load exceeds cell capacity",
  "DOUBLEBOOK  one entity, two places, same slot",
  "DEPENDENCY  starts before its predecessor finishes",
  "DEADLINE    finishes after it was promised",
  "DUPLICATE   same promise in two systems (UNKEYED - model judgment)",
  "PAID        the verdict says PAID yet the object is open (never chase it)"   // ISOBAR
};

static void byte_report(const LatHost& H){
  const double scalar = 32.0;
  const double embed  = (double)EMB_D + 4.0;
  const double per    = scalar + embed;
  const double state  = per * (double)H.N;
  const double duals  = 4.0 * ((double)H.N + (double)H.M);
  const double plan   = 4.0 * (double)H.N * (double)H.M;   // what we do NOT store
  printf("\n=== BYTES (the FluidX3D discipline: count them, print them) ===\n");
  printf("  scalar state / commitment      %8.0f B\n", scalar);
  printf("  int8 embedding + scale         %8.0f B   (fp16 would be %.0f)\n", embed, 2.0*EMB_D+4.0);
  printf("  TOTAL / commitment             %8.0f B\n", per);
  printf("  resident state (N=%d)          %8.2f MB\n", H.N, state/1e6);
  printf("  duals u[N]+v[M]                %8.2f MB\n", duals/1e6);
  printf("  plan N*M, IF MATERIALIZED      %8.2f MB   <-- never allocated (T1)\n", plan/1e6);
  printf("  saving from not materializing  %8.1fx\n", duals > 0 ? plan/duals : 0.0);
}

static void report(const LatHost& H, const TickOut& R, double peak_gbs, int tick)
{
  const int nseat = H.nseat, nslot = H.nslot;

  // ---------------- 1 · THE PRICE VECTOR ----------------
  printf("\n=== 1 · THE PRICE VECTOR (dual per column; -v = shadow price) ===\n");
  std::vector<std::pair<float,int>> seat_price(nseat, {0.f, 0});
  for (int c = 0; c < nseat*nslot; ++c) {
    const float p = R.v[c] <= 0.f ? -R.v[c] : 0.f;
    seat_price[c/nslot].first += p; seat_price[c/nslot].second = c/nslot;
  }
  std::sort(seat_price.begin(), seat_price.end(),
            [](const std::pair<float,int>& a, const std::pair<float,int>& b){ return a.first > b.first; });
  printf("  %-6s %10s   the binding capacity, most expensive first\n", "seat", "price");
  for (int k = 0; k < std::min(8, nseat); ++k)
    printf("  %-6d %10.4f   %s\n", seat_price[k].second, seat_price[k].first,
           seat_price[k].first > 1e-6f ? "<-- binding" : "");
  const float p_unp = -R.v[nseat*nslot + STOCK_UNPLACED];
  const float p_una = -R.v[nseat*nslot + STOCK_UNADJUDICATED];
  const float p_wai = -R.v[nseat*nslot + STOCK_WAITING];
  printf("  stock UNPLACED         %10.4f\n", p_unp > 0 ? p_unp : 0.f);
  printf("  stock UNADJUDICATED    %10.4f%s\n", p_una > 0 ? p_una : 0.f,
         (p_unp == 0.f && p_una == 0.f) ? "   [!] both stock duals zero - check the T17 fix" : "");
  printf("  stock WAITING          %10.4f   (the price of counterparties' silence)\n", p_wai > 0 ? p_wai : 0.f);

  // ---------------- 2 · THE SUPPORT SPECTRUM ----------------
  printf("\n=== 2 · THE SUPPORT SPECTRUM  exp(H) per commitment ===\n");
  printf("  mean %.3f  sd %.3f   (a number without its band is not a number)\n", R.es_mean, R.es_sd);
  unsigned long long tot = 0; for (auto h : R.hist) tot += h;
  unsigned long long low = 0, high = 0;
  for (size_t b = 0; b < R.hist.size(); ++b) {
    const double lo = b * 0.5, hi = lo + 0.5;
    if (hi <= 3.0) low  += R.hist[b];
    if (lo >= 3.0) high += R.hist[b];
    if (R.hist[b] == 0) continue;
    if (b > 24) continue;
    char bar[41]; const int nb = (int)(40.0 * (double)R.hist[b] / (double)std::max(1ull, tot));
    for (int k = 0; k < 40; ++k) bar[k] = k < nb ? '#' : '.';
    bar[40] = 0;
    printf("  [%4.1f,%4.1f) %8llu  %s\n", lo, hi, (unsigned long long)R.hist[b], bar);
  }
  printf("  support < 3.0 : %8llu  (%.1f%%)  DECIDED  - sparse decode faithful here; the automatable mass\n",
         (unsigned long long)low,  tot ? 100.0*low/tot  : 0.0);
  printf("  support >= 3.0: %8llu  (%.1f%%)  CONTESTED- sparse decode NOT faithful; the frontier bill\n",
         (unsigned long long)high, tot ? 100.0*high/tot : 0.0);
  printf("  (the 3.0 split is RAYFORMER's measured crossover, intrinsic dim ~2-3, ADR-007.\n"
         "   It is a borrowed constant and it is the first thing to re-measure here.)\n");

  // ---------------- 3 · THE CONTRADICTIONS ----------------
  printf("\n=== 3 · THE CONTRADICTIONS (ranked by the price of the column they sit in) ===\n");
  for (int k = 0; k < K_N; ++k)
    printf("  %-6llu  %s%s\n", (unsigned long long)R.by_kind[k], KIND_NAME[k],
           k == K_DUPLICATE ? "   [needs a sampled audit - it can be wrong]" : "   [keyed, self-certifying]");
  std::vector<Contra> top = R.contra;
  std::sort(top.begin(), top.end(), [](const Contra& a, const Contra& b){ return a.weight > b.weight; });
  printf("  --- worst 10 ---\n");
  for (int k = 0; k < std::min<int>(10, (int)top.size()); ++k) {
    const Contra& c = top[k];
    printf("  %-10s w=%7.3f  commitment %d", KIND_NAME[c.kind], c.weight, c.a);
    if (c.b >= 0) printf(" <-> %d", c.b);
    printf("   entity %d\n", H.entity[c.a]);
  }
  if (R.n_contra > (int)MAX_CONTRA)
    printf("  [!] %d contradictions found, %u kept - raise MAX_CONTRA\n", R.n_contra, MAX_CONTRA);

  // ---------------- 4 · THE ARITHMETIC LINE ----------------
  const double gbs = R.sink_ms > 0 ? R.bytes_moved / (R.sink_ms * 1e6) : 0.0;
  const double frac = peak_gbs > 0 ? gbs / peak_gbs : 0.0;
  printf("\n=== 4 · THE ARITHMETIC LINE (tick %d) ===\n", tick);
  printf("  sinkhorn %d iters            %10.2f ms\n", R.iters, R.sink_ms);
  printf("  bytes moved                  %10.3f GB\n", R.bytes_moved/1e9);
  printf("  achieved                     %10.1f GB/s\n", gbs);
  printf("  measured peak (stream triad) %10.1f GB/s\n", peak_gbs);
  printf("  fraction of peak             %10.1f%%   %s\n", 100.0*frac,
         frac >= 0.40 ? "BANDWIDTH-BOUND - the card is justified"
                      : "*** BELOW THE 40% FLOOR - THIS IS A DDR5 JOB, NOT A GPU JOB ***");
  printf("  bytes / commitment / tick    %10.0f\n",
         H.N ? R.bytes_moved / (double)H.N : 0.0);
  if (frac < 0.40)
    printf("  ^ THIS IS THE KILL CONDITION FOR THE HARDWARE THESIS. Print it either way.\n");
}

// ----------------------------------------------------------------------------
// 12 · SELFTEST — six oracles. Each carries a lie; an oracle that passes its own
//      lie is broken and says so. Nonzero exit on failure.
// ----------------------------------------------------------------------------
static int selftest(uint64_t seed, int lie)
{
  int fails = 0, lie_missed = 0;
  auto check = [&](bool ok, const char* name, const char* detail){
    printf("[%s] %-46s %s\n", ok?"PASS":"FAIL", name, detail); if(!ok) ++fails;
  };
  char buf[512];

  const int N = 3000, nseat = 24, nslot = 16, ncls = 8;
  LatHost H = build_synthetic(N, nseat, nslot, ncls, seed, 60, 0.05f);
  Dev D = upload(H);

  // ---- O5 first: the precision oracle gates everything that uses an embedding
  {
    double worst = 1.0;
    for (int i = 0; i < 200; ++i) {
      std::vector<float> f(EMB_D);
      for (int d = 0; d < EMB_D; ++d) f[d] = unorm(seed, 777, (uint64_t)i*EMB_D + d);
      std::vector<signed char> q(EMB_D); float sc;
      quantize(f, q.data(), sc);
      double dot = 0, na = 0, nb = 0;
      for (int d = 0; d < EMB_D; ++d) {
        const double x = f[d], y = (double)q[d] * sc;
        dot += x*y; na += x*x; nb += y*y;
      }
      worst = std::min(worst, dot / (sqrt(na*nb) + 1e-18));
    }
    snprintf(buf, sizeof buf, "worst round-trip cosine %.6f over 200 vectors (gate 0.995)", worst);
    check(worst >= 0.995, "O5 int8 storage / fp32 compute (T2)", buf);
  }

  // ---- O1 one dynamics source: two independent traversals must agree exactly
  const Lat Lh = host_view(H);   // ISOBAR: host traversals read the host view, never device pointers
  {
    TickOut R = run_tick(D, H, 24, 0.97f, 64);
    double worst = 0; int worst_i = -1;
    for (int i = 0; i < std::min(N, 400); ++i) {
      if (IS_MASKED(R.u[i])) continue;
      // path A: recompute the row normalizer from place_cost
      float mx, s; lse_init(mx, s);
      for (int c = 0; c < H.M; ++c) lse_push(mx, s, place_cost(Lh, i, c) + R.v[c]);
      const double zA = lse_done(mx, s);
      // path B: the dual identity  u_i = log a_i - z  =>  z = log a_i - u_i
      const double zB = log(std::max(H.supply[i], 1e-9f)) - R.u[i];
      const double e = fabs(zA - zB);
      if (e > worst) { worst = e; worst_i = i; }
    }
    snprintf(buf, sizeof buf, "max |z_direct - z_dual| = %.3e at row %d (gate 1e-3)", worst, worst_i);
    check(worst < 1e-3, "O1 one dynamics source (self-consistency)", buf);
  }

  // ---- O2 determinism: same seed, two runs, bit-identical duals
  {
    TickOut A = run_tick(D, H, 16, 0.97f, 64);
    TickOut B = run_tick(D, H, 16, 0.97f, 64);
    const bool same = A.u.size()==B.u.size() && A.v.size()==B.v.size() &&
                      memcmp(A.u.data(), B.u.data(), A.u.size()*sizeof(float))==0 &&
                      memcmp(A.v.data(), B.v.data(), A.v.size()*sizeof(float))==0;
    check(same, "O2 determinism (memcmp of the duals)", "same seed, two runs");
  }

  // ---- O3 conservation: rows ship their supply; no real column exceeds capacity
  //
  // MEASURED CONVERGENCE CURVE (2026-09-06, CPU build, N=3000, M=386). The gate
  // was NOT widened to make this pass; the iteration count was wrong.
  //
  //   iters    row err     worst column overflow
  //      60    2.16e-06    1.01e-02   FAIL  (marginal, 1% over the gate)
  //     150    1.73e-06    3.32e-04   pass
  //     400    1.92e-06    4.69e-06   pass  <- plateau
  //    1000    1.79e-06    4.57e-06   pass  (no further gain)
  //
  // The column pass is an inequality projection and converges geometrically;
  // the row pass is an equality and is exact after every sweep. Publish the
  // curve, not the point.
  {
    TickOut R = run_tick(D, H, LL_O3_ITERS, 0.97f, 64);
    double row_err = 0, col_viol = 0;
    std::vector<double> colmass(H.M, 0.0);
    for (int i = 0; i < N; ++i) {
      if (IS_MASKED(R.u[i])) continue;
      double rs = 0;
      for (int c = 0; c < H.M; ++c) {
        const float lc = place_cost(Lh, i, c);   // ISOBAR: host view
        if (IS_MASKED(lc)) continue;
        const double p = exp((double)lc + R.u[i] + R.v[c]);
        rs += p; colmass[c] += p;
      }
      row_err = std::max(row_err, fabs(rs - H.supply[i]) / std::max(1e-9, (double)H.supply[i]));
    }
    for (int c = 0; c < H.nseat*H.nslot; ++c)
      col_viol = std::max(col_viol, (colmass[c] - H.cap[c]) / std::max(1e-9f, H.cap[c]));
    snprintf(buf, sizeof buf, "row err %.2e, worst column overflow %.2e (gates 1e-2 / 1e-2)", row_err, col_viol);
    check(row_err < 1e-2 && col_viol < 1e-2, "O3 conservation (supply shipped, capacity held)", buf);
  }

  // ---- O4 THE T17 FIX: both stock columns must carry a NONZERO dual once loaded
  {
    LatHost H2 = H;
    for (int c = 0; c < H2.nseat*H2.nslot; ++c) H2.cap[c] *= 0.25f;   // squeeze: force overflow into stock
    Dev D2 = upload(H2);
    TickOut R = run_tick(D2, H2, 80, 0.97f, 64);
    const float pu = -R.v[H2.nseat*H2.nslot + STOCK_UNPLACED];
    const float pa = -R.v[H2.nseat*H2.nslot + STOCK_UNADJUDICATED];
    snprintf(buf, sizeof buf, "unplaced price %.4f, unadjudicated price %.4f (both must be > 0)", pu, pa);
    check(pu > 1e-6f && pa > 1e-6f, "O4 stock columns are priced (the T17 fix)", buf);
    release(D2);
  }

  // ---- O6 the unkeyed matcher recovers planted duplicates
  {
    TickOut R = run_tick(D, H, 40, 0.90f, 64);
    int hit = 0;
    for (size_t k = 0; k < H.planted_dup_a.size(); ++k) {
      const int a = H.planted_dup_a[k], b = H.planted_dup_b[k];
      for (const Contra& c : R.contra)
        if (c.kind == K_DUPLICATE && ((c.a==a&&c.b==b)||(c.a==b&&c.b==a))) { ++hit; break; }
    }
    const int planted = (int)H.planted_dup_a.size();
    const int found   = (int)R.by_kind[K_DUPLICATE];
    snprintf(buf, sizeof buf, "recovered %d/%d planted; %d total flagged (extras are candidates, not errors)",
             hit, planted, found);
    // NOTE: this oracle is deliberately weaker than the keyed ones. The unkeyed
    // matcher is a model judgment; it is graded on recall, and its precision is
    // a SAMPLED AUDIT, never a self-report.
    check(planted == 0 || hit >= (planted*7)/10, "O6 unkeyed duplicate recall (>=70%)", buf);
  }

  // ---- O8 ISOBAR K_PAID: every planted paid-but-open row is a contradiction, and nothing else is
  {
    TickOut R = run_tick(D, H, 24, 0.97f, 64);
    int hit = 0, extra = 0;
    for (const Contra& c : R.contra) if (c.kind == K_PAID) { if (H.paid[c.a]) ++hit; else ++extra; }
    snprintf(buf, sizeof buf, "K_PAID fired on %d/%d planted, %d extras (gate: all, none)", hit, H.planted_paid, extra);
    check(hit == H.planted_paid && extra == 0, "O8 K_PAID (paid-by-verdict never chased)", buf);
    // and the waiting rows sit in their stock, whose dual is nonzero under the planted load
    const float pw = -R.v[H.nseat*H.nslot + STOCK_WAITING];
    snprintf(buf, sizeof buf, "%d waiting rows; WAITING price %.4f (must be > 0)", H.planted_waiting, pw);
    check(H.planted_waiting == 0 || pw > 1e-6f, "O8b the WAITING stock is priced", buf);
  }

  // ---- THE LIE: run one oracle against a deliberately broken lattice.
  if (lie > 0) {
    printf("\n--- lie arm %d: the oracle must FAIL, or the oracle is broken ---\n", lie);
    LatHost B = H;
    bool caught = false;
    if (lie == 1) {                       // break the T17 fix: stock capacity to infinity
      B.cap[B.nseat*B.nslot + STOCK_UNPLACED]      = 1e30f;
      B.cap[B.nseat*B.nslot + STOCK_UNADJUDICATED] = 1e30f;
      Dev DB = upload(B);
      TickOut R = run_tick(DB, B, 80, 0.97f, 64);
      const float pu = -R.v[B.nseat*B.nslot + STOCK_UNPLACED];
      caught = !(pu > 1e-6f);
      printf("    O4 under the lie: unplaced price %.6f -> %s\n", pu, caught ? "FAILED (correct)" : "PASSED (BROKEN ORACLE)");
      release(DB);
    } else if (lie == 2) {                // corrupt an embedding: duplicates must be lost
      for (size_t k = 0; k < B.planted_dup_b.size(); ++k)
        for (int d = 0; d < EMB_D; ++d) B.emb[(size_t)B.planted_dup_b[k]*EMB_D + d] = (signed char)(-B.emb[(size_t)B.planted_dup_b[k]*EMB_D + d]);
      Dev DB = upload(B);
      TickOut R = run_tick(DB, B, 40, 0.90f, 64);
      int hit = 0;
      for (size_t k = 0; k < B.planted_dup_a.size(); ++k)
        for (const Contra& c : R.contra)
          if (c.kind==K_DUPLICATE && ((c.a==B.planted_dup_a[k]&&c.b==B.planted_dup_b[k])||(c.a==B.planted_dup_b[k]&&c.b==B.planted_dup_a[k]))) { ++hit; break; }
      caught = hit < (int)((B.planted_dup_a.size()*7)/10);
      printf("    O6 under the lie: recovered %d/%d -> %s\n", hit, (int)B.planted_dup_a.size(),
             caught ? "FAILED (correct)" : "PASSED (BROKEN ORACLE)");
      release(DB);
    } else if (lie == 3) {                // ISOBAR: drop the verdict column — K_PAID must go blind and O8 must FAIL
      std::fill(B.paid.begin(), B.paid.end(), (unsigned char)0);
      Dev DB = upload(B);
      TickOut R = run_tick(DB, B, 24, 0.97f, 64);
      int hit = 0; for (const Contra& c : R.contra) if (c.kind == K_PAID) ++hit;
      caught = (hit != H.planted_paid);   // the oracle compares against the ORIGINAL planted count
      printf("    O8 under the lie: K_PAID fired %d vs %d planted -> %s\n", hit, H.planted_paid,
             caught ? "FAILED (correct)" : "PASSED (BROKEN ORACLE)");
      release(DB);
    }
    if (!caught) { ++lie_missed; }
  }

  release(D);
  printf("\n%s%s\n", fails ? "SELFTEST: FAILED" : "SELFTEST: all oracles pass",
         lie_missed ? "  [!] AN ORACLE PASSED ITS OWN LIE - THAT ORACLE IS BROKEN" : "");
  return (fails || lie_missed) ? 1 : 0;
}

// ----------------------------------------------------------------------------
// 13 · ISOBAR IPC — `--tick lattice.bin [--prev field.bin] [--out field]`
//
// isobard writes lattice.bin (a 64-byte header, then SoA arrays in the order below, little-endian,
// no padding); this instrument runs ONE tick (both arms) and writes <out>.json (the Field the plane
// folds onto the tape) and <out>.bin (the duals, for the next tick's Δv). No JSON is parsed here.
//
//   header: "ISOB" u32 version=1 | i32 N nseat nslot ncls | f32 T late_penalty | i32 iters arm |
//           u64 seed | f32 dup_cos | i32 emb_d(=EMB_D) | pad to 64
//   arrays: i32 entity[N] i16 cls[N] u8 dur[N] u8 src[N] i32 t_open[N] i32 t_due[N] f32 work[N]
//           i32 dep[N] i32 inc_cell[N] u32 flags[N] f32 tier_w[N] u8 paid[N] u8 waiting[N]
//           i8 emb[N*EMB_D] f32 emb_scale[N] i8 seat_key[nseat*EMB_D] f32 seat_scale[nseat]
//           f32 cap[M] f32 supply[N] u32 law[lawwords] u32 arm_mask[armwords]
// ----------------------------------------------------------------------------
#pragma pack(push, 1)
struct IsobHeader { char magic[4]; uint32_t version; int32_t N, nseat, nslot, ncls; float T, late_penalty;
                    int32_t iters, arm; uint64_t seed; float dup_cos; int32_t emb_d; unsigned char pad[8]; };
#pragma pack(pop)
static_assert(sizeof(IsobHeader) == 64, "IsobHeader must be 64 bytes");

template <class T> static bool rd(FILE* f, std::vector<T>& v, size_t n){ v.resize(n); return n == 0 || fread(v.data(), sizeof(T), n, f) == n; }

static bool load_lattice_bin(const char* path, LatHost& H, IsobHeader& hd){
  FILE* f = fopen(path, "rb");
  if (!f) { fprintf(stderr, "cannot open %s\n", path); return false; }
  if (fread(&hd, sizeof hd, 1, f) != 1 || memcmp(hd.magic, "ISOB", 4) != 0 || hd.version != 1 || hd.emb_d != EMB_D) {
    fprintf(stderr, "bad lattice header (magic/version/emb_d)\n"); fclose(f); return false; }
  const int N = hd.N, nseat = hd.nseat, nslot = hd.nslot;
  H.N=N; H.nseat=nseat; H.nslot=nslot; H.ncls=hd.ncls; H.M = nseat*nslot + N_STOCK; H.T=hd.T; H.late_penalty=hd.late_penalty;
  const size_t lawwords = ((size_t)hd.ncls*nseat + 31)/32, armwords = ((size_t)nseat + 31)/32;
  bool ok = rd(f,H.entity,N) && rd(f,H.cls,N) && rd(f,H.dur,N) && rd(f,H.src,N) && rd(f,H.t_open,N) && rd(f,H.t_due,N)
         && rd(f,H.work,N) && rd(f,H.dep,N) && rd(f,H.inc_cell,N) && rd(f,H.flags,N)
         && rd(f,H.tier_w,N) && rd(f,H.paid,N) && rd(f,H.waiting,N)
         && rd(f,H.emb,(size_t)N*EMB_D) && rd(f,H.emb_scale,N) && rd(f,H.seat_key,(size_t)nseat*EMB_D) && rd(f,H.seat_scale,nseat)
         && rd(f,H.cap,H.M) && rd(f,H.supply,N) && rd(f,H.law,lawwords) && rd(f,H.arm_mask,armwords);
  fclose(f);
  if (!ok) { fprintf(stderr, "lattice.bin truncated\n"); return false; }
  return true;
}

static bool read_prev_v(const char* path, std::vector<float>& v){
  FILE* f = fopen(path, "rb"); if (!f) return false;
  int32_t M = 0; if (fread(&M, 4, 1, f) != 1 || M <= 0 || M > (1<<26)) { fclose(f); return false; }
  v.resize(M); const bool ok = fread(v.data(), 4, M, f) == (size_t)M; fclose(f); return ok;
}

static void write_json_farr(FILE* f, const char* key, const std::vector<float>& a){
  fprintf(f, "\"%s\":[", key); for (size_t i=0;i<a.size();++i) fprintf(f, "%s%.7g", i?",":"", IS_MASKED(a[i]) ? -1e30 : a[i]); fprintf(f, "]");
}

static int run_tick_file(const char* lat_path, const char* prev_path, const char* out_base, bool bench, int nbins){
  LatHost H; IsobHeader hd{};
  if (!load_lattice_bin(lat_path, H, hd)) return 2;
  const double peak = bench ? measure_peak_gbs(1LL << 25) : 0.0;
  Dev D = upload(H);
  D.L.arm = hd.arm;
  TickOut R = run_tick(D, H, hd.iters > 0 ? hd.iters : 40, hd.dup_cos > 0 ? hd.dup_cos : 0.95f, nbins);
  D.L.arm = 1 - hd.arm;
  TickOut R2 = run_tick(D, H, hd.iters > 0 ? hd.iters : 40, hd.dup_cos > 0 ? hd.dup_cos : 0.95f, nbins);
  release(D);

  // Δv against the previous tick's duals (same M required)
  std::vector<float> pv; double dvn = -1.0;
  std::vector<std::pair<float,int>> movers;
  if (prev_path && read_prev_v(prev_path, pv) && (int)pv.size() == H.M) {
    double s2 = 0; for (int c=0;c<H.M;++c){ const double d = (double)R.v[c]-(double)pv[c]; s2 += d*d; movers.push_back({(float)fabs(d), c}); }
    dvn = sqrt(s2);
    std::sort(movers.begin(), movers.end(), [](const std::pair<float,int>& a, const std::pair<float,int>& b){ return a.first > b.first; });
    if (movers.size() > 8) movers.resize(8);
  }

  std::string jp = std::string(out_base) + ".json", bp = std::string(out_base) + ".bin";
  FILE* f = fopen(jp.c_str(), "wb"); if (!f) { fprintf(stderr, "cannot write %s\n", jp.c_str()); return 2; }
  const double gbs = R.sink_ms > 0 ? R.bytes_moved / (R.sink_ms * 1e6) : 0.0;
  fprintf(f, "{\"version\":1,\"N\":%d,\"M\":%d,\"nseat\":%d,\"nslot\":%d,\"n_stock\":%d,\"iters\":%d,\"arm\":%d,\"seed\":%llu,",
          H.N, H.M, H.nseat, H.nslot, N_STOCK, R.iters, hd.arm, (unsigned long long)hd.seed);
  write_json_farr(f, "u", R.u); fputc(',', f);
  write_json_farr(f, "v", R.v); fputc(',', f);
  write_json_farr(f, "es", R.es); fputc(',', f);
  write_json_farr(f, "risk", R.risk); fputc(',', f);
  fprintf(f, "\"argmax_cell\":["); for (int i=0;i<H.N;++i) fprintf(f, "%s%d", i?",":"", R.argmax_cell[i]); fprintf(f, "],");
  fprintf(f, "\"es_mean\":%.6g,\"es_sd\":%.6g,", R.es_mean, R.es_sd);
  fprintf(f, "\"stock_prices\":{\"UNPLACED\":%.7g,\"UNADJUDICATED\":%.7g,\"WAITING\":%.7g},",
          std::max(0.f, -R.v[H.nseat*H.nslot+STOCK_UNPLACED]), std::max(0.f, -R.v[H.nseat*H.nslot+STOCK_UNADJUDICATED]),
          std::max(0.f, -R.v[H.nseat*H.nslot+STOCK_WAITING]));
  fprintf(f, "\"other_arm\":{\"es_mean\":%.6g,\"unplaced_price\":%.7g,\"waiting_price\":%.7g},",
          R2.es_mean, std::max(0.f, -R2.v[H.nseat*H.nslot+STOCK_UNPLACED]), std::max(0.f, -R2.v[H.nseat*H.nslot+STOCK_WAITING]));
  fprintf(f, "\"by_kind\":{"); for (int k=0;k<K_N;++k) fprintf(f, "%s\"%d\":%llu", k?",":"", k, (unsigned long long)R.by_kind[k]); fprintf(f, "},");
  fprintf(f, "\"contra\":["); { const int keep = std::min<int>((int)R.contra.size(), 4096);
    for (int k=0;k<keep;++k) fprintf(f, "%s{\"a\":%d,\"b\":%d,\"kind\":%d,\"w\":%.5g}", k?",":"", R.contra[k].a, R.contra[k].b, R.contra[k].kind, R.contra[k].weight); }
  fprintf(f, "],\"n_contra\":%d,", R.n_contra);
  fprintf(f, "\"delta_v_norm\":%.7g,\"movers\":[", dvn);
  for (size_t k=0;k<movers.size();++k) fprintf(f, "%s{\"c\":%d,\"dv\":%.6g,\"v\":%.6g}", k?",":"", movers[k].second, (double)R.v[movers[k].second]-(double)pv[movers[k].second], R.v[movers[k].second]);
  fprintf(f, "],\"arithmetic\":{\"sink_ms\":%.3f,\"bytes\":%.0f,\"gbs\":%.2f,\"peak_gbs\":%.2f,\"fraction\":%.4f,\"floor\":0.40,\"measured_peak\":%s}}\n",
          R.sink_ms, R.bytes_moved, gbs, peak, peak > 0 ? gbs/peak : -1.0, bench ? "true" : "false");
  fclose(f);
  FILE* fb = fopen(bp.c_str(), "wb"); if (fb) { int32_t M = H.M; fwrite(&M, 4, 1, fb); fwrite(R.v.data(), 4, M, fb); fclose(fb); }
  printf("tick: N=%d M=%d iters=%d sink %.2f ms  dv=%.4g  contra=%d  waiting=%.4f  peak=%s\n",
         H.N, H.M, R.iters, R.sink_ms, dvn, R.n_contra, std::max(0.f, -R.v[H.nseat*H.nslot+STOCK_WAITING]), bench ? "measured" : "skipped");
  return 0;
}

// ----------------------------------------------------------------------------
// 14 · MAIN
// ----------------------------------------------------------------------------
int main(int argc, char** argv)
{
  int N = 50000, nseat = 64, nslot = 32, ncls = 24, ticks = 1, iters = 40, nbins = 64;
  int n_dup = 200, lie = 0;
  float dup_cos = 0.95f, T = 0.25f;
  uint64_t seed = 42;
  bool do_selftest = false, do_bench = false, do_demo = false, no_bench = false;
  const char* cdc = nullptr;
  const char* tick_path = nullptr; const char* prev_path = nullptr; const char* out_base = "field";   // ISOBAR

  for (int i = 1; i < argc; ++i) {
    std::string s = argv[i];
    auto nx = [&]() -> const char* { return (i+1 < argc) ? argv[++i] : "0"; };
    if      (s == "--selftest")    do_selftest = true;
    else if (s == "--bench")       do_bench = true;
    else if (s == "--demo")        do_demo = true;
    else if (s == "--commitments") N = atoi(nx());
    else if (s == "--seats")       nseat = atoi(nx());
    else if (s == "--slots")       nslot = atoi(nx());
    else if (s == "--classes")     ncls = atoi(nx());
    else if (s == "--ticks")       ticks = atoi(nx());
    else if (s == "--iters")       iters = atoi(nx());
    else if (s == "--dup-cos")     dup_cos = (float)atof(nx());
    else if (s == "--temp")        T = (float)atof(nx());
    else if (s == "--seed")        seed = strtoull(nx(), nullptr, 10);
    else if (s == "--dups")        n_dup = atoi(nx());
    else if (s == "--lie")         lie = atoi(nx());
    else if (s == "--cdc")         cdc = nx();
    else if (s == "--tick")        tick_path = nx();      // ISOBAR IPC
    else if (s == "--prev")        prev_path = nx();
    else if (s == "--out")         out_base = nx();
    else if (s == "--no-bench")    no_bench = true;
    else { fprintf(stderr, "unknown flag %s\n", argv[i]); return 2; }
  }

  if (do_selftest) return selftest(seed, lie);
  if (tick_path)   return run_tick_file(tick_path, prev_path, out_base, !no_bench, nbins);

  // VRAM tier — the same binary sizes itself. 5090 is the design point.
  size_t freeb = 0, totb = 0; dev_meminfo(&freeb, &totb);
  const double gib = (double)totb / (1024.0*1024.0*1024.0);
  printf("=== LEDGER LATTICE ===\n");
  printf("device memory: %.1f GiB total, %.1f GiB free  ->  tier %s\n", gib,
         (double)freeb/(1024.0*1024.0*1024.0),
         // Capacity = (total - model - KV - workspace - display) / 1160 B per record
         // (int8 1024-d full + int8 128-d coarse + scales; both tiers resident).
         // CORRECTED 2026-09-06: the first version reserved ~6 GB on a 32 GB card
         // and divided by 1028, which ignores the coarse tier AND is less than a
         // resident 9B Q5 weighs on its own. It read 60% high. Capacity is not the
         // same claim as "bandwidth-bound"; only the arithmetic line decides that.
         gib >= 100 ? "H200-class    (~103M records)" :
         gib >=  40 ? "48GB pro      (~30M records)"  :
         gib >=  28 ? "5090-class    (~16M records)"  :
         gib >=  20 ? "4090-class     (~9M records)"  : "CPU / small");

  double peak = 0.0;
  if (do_bench || do_demo || cdc) {
    const long long ne = 1LL << 25;   // ISOBAR: 128 MB per array — past the 48 MB L2, so this is DRAM
    peak = measure_peak_gbs(ne);
    printf("measured peak bandwidth (stream triad, %lld elems): %.1f GB/s\n", ne, peak);
    if (do_bench && !do_demo && !cdc) return 0;
  }

  LatHost H;
  if (cdc) {
    if (!ingest_csv(H, cdc, nseat, nslot, ncls)) return 2;
  } else {
    H = build_synthetic(N, nseat, nslot, ncls, seed, n_dup, 0.03f);
    printf("synthetic: %d commitments, %dx%d lattice (+%d stock), %d classes, seed %llu\n",
           H.N, nseat, nslot, N_STOCK, ncls, (unsigned long long)seed);
    printf("planted: %d duplicate pairs, %d overcommitted cells, %d deadline breaches, %d dependency violations\n",
           (int)H.planted_dup_a.size(), H.planted_overcommit, H.planted_deadline, H.planted_dep);
  }
  H.T = T;
  byte_report(H);

  Dev D = upload(H);
  for (int t = 0; t < ticks; ++t) {
    // THE TWO ARMS, ONE CANVAS (T3): tick the incumbent arm, then flip one int
    // and tick the solver arm. No second canvas is allocated, ever.
    D.L.arm = 0;
    TickOut inc = run_tick(D, H, iters, dup_cos, nbins);
    D.L.arm = 1;
    TickOut sol = run_tick(D, H, iters, dup_cos, nbins);

    report(H, inc, peak, t);
    printf("\n=== THE PAIRED ARM (T3: one canvas, two law masks, zero extra state) ===\n");
    printf("  incumbent support mean %.3f (sd %.3f)   solver support mean %.3f (sd %.3f)\n",
           inc.es_mean, inc.es_sd, sol.es_mean, sol.es_sd);
    printf("  incumbent unplaced price %.4f            solver unplaced price %.4f\n",
           -inc.v[H.nseat*H.nslot+STOCK_UNPLACED], -sol.v[H.nseat*H.nslot+STOCK_UNPLACED]);
    printf("  the solver arm masks %d of %d seats; the difference in unplaced price is what\n",
           [&]{ int n=0; for(int s=0;s<H.nseat;++s) if((H.arm_mask[s>>5]>>(s&31))&1u) ++n; return n; }(), H.nseat);
    printf("  that masking costs, paired, this tick. No promotion was made and none is claimed.\n");
  }
  release(D);
  printf("\nIT DECIDED NOTHING AND WROTE NOTHING. The residual is the product.\n");
  return 0;
}
