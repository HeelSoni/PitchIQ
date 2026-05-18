import { create } from 'zustand';
import axios from 'axios';
import { API_BASE } from '../config';

export interface Startup {
  id: number;
  name: string;
  slug: string;
  industry: string;
  business_model: string;
  season: number;
  founder_names: string[];
  founder_background: string;
  description: string;
  website: string;
  logo_url: string | null;
  deal: {
    ask_amount: number | null;
    ask_equity: number | null;
    ask_valuation: number | null;
    final_deal_amount: number | null;
    final_equity: number | null;
    final_valuation: number | null;
    deal_status: string;
    royalty: number | null;
    debt_component: number | null;
    notes: string | null;
  } | null;
  financials: Array<{
    revenue: number | null;
    profit: number | null;
    ebitda: number | null;
    gross_margin: number | null;
    net_margin: number | null;
    ebitda_margin: number | null;
    burn_rate: number | null;
    runway: number | null;
    debt: number | null;
  }>;
  shark_deals: Array<{
    shark: {
      id: number;
      name: string;
      company: string;
      title: string;
    };
    amount_invested: number | null;
    equity_taken: number | null;
  }>;
  health_score?: {
    total: number;
    breakdown: {
      growth: number;
      profitability: number;
      margins: number;
      market_size: number;
      founder_strength: number;
    }
  };
  ai_insight?: string;
}

export interface Shark {
  id: number;
  name: string;
  company: string;
  title: string;
  bio: string;
  net_worth: string;
  expertise: string[];
  seasons: number[];
  image_url: string | null;
  stats: {
    total_deals: number;
    total_invested_lakhs: number;
    avg_equity_percent: number;
    avg_ticket_size_lakhs: number;
    favorite_industries: string[];
  };
}

interface PitchState {
  startups: Startup[];
  industries: string[];
  sharks: Shark[];
  stats: {
    total_pitches: number;
    total_deals: number;
    total_investment: number;
    success_rate: number;
  } | null;
  loading: boolean;
  filters: {
    search: string;
    industry: string;
    season: string;
    deal_status: string;
    shark_id: string;
    profitable: boolean;
    revenue_gt_1cr: boolean;
    margin_gt_30: boolean;
    order_by: string;
  };
  setFilter: (key: string, value: any) => void;
  resetFilters: () => void;
  fetchStartups: () => Promise<void>;
  fetchIndustries: () => Promise<void>;
  fetchSharks: () => Promise<void>;
  fetchStats: () => Promise<void>;
}

export const usePitchStore = create<PitchState>((set, get) => ({
  startups: [],
  industries: [],
  sharks: [],
  stats: null,
  loading: false,
  filters: {
    search: '',
    industry: '',
    season: '',
    deal_status: '',
    shark_id: '',
    profitable: false,
    revenue_gt_1cr: false,
    margin_gt_30: false,
    order_by: 'name',
  },

  setFilter: (key, value) => {
    set((state) => ({
      filters: { ...state.filters, [key]: value },
    }));
    get().fetchStartups();
  },

  resetFilters: () => {
    set({
      filters: {
        search: '',
        industry: '',
        season: '',
        deal_status: '',
        shark_id: '',
        profitable: false,
        revenue_gt_1cr: false,
        margin_gt_30: false,
        order_by: 'name',
      },
    });
    get().fetchStartups();
  },

  fetchStartups: async () => {
    set({ loading: true });
    try {
      const f = get().filters;
      const params: any = {};
      if (f.search) params.search = f.search;
      if (f.industry) params.industry = f.industry;
      if (f.season) params.season = Number(f.season);
      if (f.deal_status) params.deal_status = f.deal_status;
      if (f.shark_id) params.shark_id = Number(f.shark_id);
      if (f.profitable) params.profitable = true;
      if (f.revenue_gt_1cr) params.revenue_gt_1cr = true;
      if (f.margin_gt_30) params.margin_gt_30 = true;
      params.order_by = f.order_by;

      const res = await axios.get(`${API_BASE}/startups/`, { params });
      set({ startups: res.data });
    } catch (err) {
      console.error(err);
    } finally {
      set({ loading: false });
    }
  },

  fetchIndustries: async () => {
    try {
      const res = await axios.get(`${API_BASE}/startups/industries`);
      set({ industries: res.data });
    } catch (err) {
      console.error(err);
    }
  },

  fetchSharks: async () => {
    try {
      const res = await axios.get(`${API_BASE}/sharks/`);
      set({ sharks: res.data });
    } catch (err) {
      console.error(err);
    }
  },

  fetchStats: async () => {
    try {
      const res = await axios.get(`${API_BASE}/startups/stats`);
      set({ stats: res.data });
    } catch (err) {
      console.error(err);
    }
  },
}));
