#define KBUILD_MODNAME "tcpcctrace"
#include <uapi/linux/ptrace.h>
#include <net/sock.h>
#include <bcc/proto.h>
#include <net/tcp.h>

struct bbr {
	u32	min_rtt_us;	        /* min RTT in min_rtt_win_sec window */
	u32	min_rtt_stamp;	        /* timestamp of min_rtt_us */
	u32	probe_rtt_done_stamp;   /* end time for BBR_PROBE_RTT mode */
	u32	rtt_cnt;	    /* count of packet-timed rounds elapsed */
	u32     next_rtt_delivered; /* scb->tx.delivered at end of round */
	u64	cycle_mstamp;	     /* time of this cycle phase start */
	u32     mode:3,		     /* current bbr_mode in state machine */
		prev_ca_state:3,     /* CA state on previous ACK */
		packet_conservation:1,  /* use packet conservation? */
		round_start:1,	     /* start of packet-timed tx->ack round? */
		idle_restart:1,	     /* restarting after idle? */
		probe_rtt_round_done:1,  /* a BBR_PROBE_RTT round at 4 pkts? */
		unused:13,
		lt_is_sampling:1,    /* taking long-term ("LT") samples now? */
		lt_rtt_cnt:7,	     /* round trips in long-term interval */
		lt_use_bw:1;	     /* use lt_bw as our bw estimate? */
	u32	lt_bw;		     /* LT est delivery rate in pkts/uS << 24 */
	u32	lt_last_delivered;   /* LT intvl start: tp->delivered */
	u32	lt_last_stamp;	     /* LT intvl start: tp->delivered_mstamp */
	u32	lt_last_lost;	     /* LT intvl start: tp->lost */
	u32	pacing_gain:10,	/* current gain for setting pacing rate */
		cwnd_gain:10,	/* current gain for setting cwnd */
		full_bw_reached:1,   /* reached full bw in Startup? */
		full_bw_cnt:2,	/* number of rounds without large bw gains */
		cycle_idx:3,	/* current index in pacing_gain cycle array */
		has_seen_rtt:1, /* have we seen an RTT sample yet? */
		unused_b:5;
	u32	prior_cwnd;	/* prior cwnd upon entering loss recovery */
	u32	full_bw;	/* recent bw, to estimate if pipe is full */
};

struct congestion_info {
	u64 timestamp;
	u32 saddr;
	u32 daddr;
	u16 sport;
    u16 dport;
    u32 snd_cwnd;
	u32 min_rtt;
	u32 smoothed_rtt;
	u32 latest_rtt;
	u64 bytes_sent;
	u64 bytes_acked;
	u32 ssthresh;
};
BPF_PERF_OUTPUT(tcp_events);


void trace_rcv_established(struct pt_regs *ctx, struct sock *sk)
{
	u16 family = sk->__sk_common.skc_family;
	if (family == AF_INET) {
    	struct congestion_info info = {};
		info.saddr = sk->__sk_common.skc_rcv_saddr;
		info.daddr = sk->__sk_common.skc_daddr;
		info.sport = sk->__sk_common.skc_num;
		u16 dport = sk->__sk_common.skc_dport;
		info.dport = ntohs(dport);
    	const struct tcp_sock *tp = tcp_sk(sk);
    	info.snd_cwnd = tp->snd_cwnd; //Sending congestion window
		info.min_rtt = tp->rtt_min.s[0].v;
		info.smoothed_rtt = tp->srtt_us >> 3; //smoothed round trip time << 3 in usecs
		info.latest_rtt = tp->rack.rtt_us; // Information of the most recently (s)acked skb
		info.bytes_sent = tp->bytes_sent;
		info.bytes_acked = tp->bytes_acked;
		info.ssthresh = tp->snd_ssthresh; //Slow start size threshold

		info.timestamp = bpf_ktime_get_ns();
    	tcp_events.perf_submit(ctx, &info, sizeof(info));
	}
}

void trace_statechange(struct pt_regs *ctx, struct sock *sk) {

}