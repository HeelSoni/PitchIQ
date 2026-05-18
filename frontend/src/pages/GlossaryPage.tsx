import React, { useState } from 'react';
import { HelpCircle, Search, Sparkles } from 'lucide-react';

export default function GlossaryPage() {
  const [search, setSearch] = useState('');

  const terms = [
    {
      term: 'Revenue',
      def: 'The total amount of money brought in by a company through sales of its goods or services before expenses are deducted.',
      example: 'Skippi Ice Pops pitching their Yearly Revenue of ₹21 Lakhs during Season 1.'
    },
    {
      term: 'Profit',
      def: 'The financial gain representing the difference between the revenue earned and expenses paid.',
      example: 'Startups showing "profitable" operations, giving comfort to Namita and Anupam.'
    },
    {
      term: 'EBITDA',
      def: 'Earnings Before Interest, Taxes, Depreciation, and Amortization. A proxy for operational cash flow profitability.',
      example: 'Namita asking: "Aapka EBITDA positive kab hoga?" to calculate core operational health.'
    },
    {
      term: 'Valuation',
      def: 'The analytical estimation of the total financial worth of a company.',
      example: 'A startup asking for ₹50 Lakhs for 5% equity implies a ₹10 Crore (1000 Lakhs) Valuation.'
    },
    {
      term: 'Equity',
      def: 'The percentage ownership of a startup held by founders or sold to investors.',
      example: 'Aman negotiating for 15% equity instead of the initial 5% offer.'
    },
    {
      term: 'Burn Rate',
      def: 'The rate at which a company loses money, typically expressed on a monthly basis, when costs exceed revenues.',
      example: 'Peyush asks: "Monthly cash burn kitna hai?" to evaluate cash consumption velocity.'
    },
    {
      term: 'Runway',
      def: 'The length of time a startup can continue to operate at its current burn rate before running out of capital.',
      example: 'A startup with ₹60 Lakhs in cash and a monthly burn of ₹5 Lakhs has a 12-month Runway.'
    },
    {
      term: 'CAC',
      def: 'Customer Acquisition Cost. The total cost associated with acquiring a single new customer.',
      example: 'Vineeta questioning a D2C makeup startup on Facebook ad CAC vs product pricing.'
    },
    {
      term: 'LTV',
      def: 'Lifetime Value. The total value or revenue a single customer brings to a business over their active relationship lifetime.',
      example: 'Anupam calculated the LTV/CAC ratio to see if high customer acquisition cost is justified.'
    },
    {
      term: 'Gross Margin',
      def: 'The percentage of revenue that remains after deducting the Direct Cost of Goods Sold (COGS).',
      example: 'FMCG food pitches usually have 40-50% gross margins, while SaaS brands enjoy 80%+.'
    },
    {
      term: 'Net Margin',
      def: 'The percentage of revenue left over after all operating expenses, interest, and taxes are paid.',
      example: 'A startup with ₹1 Cr revenue and ₹15 Lakhs net profit has a 15% net margin profile.'
    },
    {
      term: 'Dilution',
      def: 'The reduction in ownership percentage for existing founders when new equity is issued to investors.',
      example: 'Founders diluting 20% of their equity to a syndicated shark group to secure key distribution.'
    },
    {
      term: 'AOV',
      def: 'Average Order Value. The average amount of money a customer spends per transaction on an e-commerce platform.',
      example: 'Vineeta analyzing a D2C fashion brand to see if an AOV of ₹1,200 supports digital ad costs.'
    },
    {
      term: 'Repeat Rate',
      def: 'The percentage of customers who return to make a second or subsequent purchase within a given timeframe.',
      example: 'A high 40% monthly Repeat Rate for a coffee startup highlights strong customer loyalty.'
    },
    {
      term: 'D2C',
      def: 'Direct-to-Consumer. A retail channel strategy where a brand sells directly to consumers through web stores, skipping wholesalers.',
      example: 'SUGAR Cosmetics or boAt represent Indian D2C giants built on direct digital acquisition.'
    },
    {
      term: 'SaaS',
      def: 'Software-as-a-Service. A licensing and distribution model where software is hosted and paid for on a subscription base.',
      example: 'Logistics and HR management software startups pitching high-recurring annual contracts.'
    },
    {
      term: 'Burn Multiple',
      def: 'The ratio of net cash burned relative to Net New ARR generated. Measures operational efficiency.',
      example: 'Anupam analyzing if a SaaS startup is burning ₹3 to generate ₹1 of new contract revenue.'
    }
  ];

  const filtered = terms.filter(t => 
    t.term.toLowerCase().includes(search.toLowerCase()) || 
    t.def.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10 space-y-12">
      <div className="space-y-4 max-w-3xl">
        <h1 className="text-3xl sm:text-5xl font-extrabold tracking-tight font-Outfit">
          Financial{' '}
          <span className="bg-gradient-to-r from-cyan-400 to-cyan-300 bg-clip-text text-transparent">
            Glossary
          </span>
        </h1>
        <p className="text-text-secondary text-sm sm:text-base">
          Master the financial vocabulary used on the show. Explore definitions, operational ratios, and real examples from actual Shark Tank India pitches.
        </p>
      </div>

      {/* Search Input */}
      <div className="glass p-4 rounded-2xl border border-white/5 relative max-w-md">
        <Search className="absolute left-4 top-5 w-4 h-4 text-text-secondary" />
        <input
          type="text"
          placeholder="Search glossary terms..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="w-full bg-white/5 border border-white/5 rounded-xl pl-10 pr-4 py-2 text-xs focus:outline-none focus:border-accent/50 text-text-primary"
        />
      </div>

      {/* Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {filtered.map((item, idx) => (
          <div key={idx} className="glass p-6 rounded-3xl border border-white/5 flex flex-col justify-between hover-lift">
            <div className="space-y-3">
              <span className="text-[9px] font-bold text-accent uppercase bg-accent/10 px-2 py-0.5 rounded-full">
                Financial Ratio
              </span>
              <h3 className="text-lg font-bold font-Outfit text-text-primary">{item.term}</h3>
              <p className="text-text-secondary text-xs leading-relaxed">
                {item.def}
              </p>
            </div>

            {/* Real example panel */}
            <div className="mt-4 pt-3 border-t border-white/5 text-[11px] text-accent flex items-start space-x-1.5">
              <Sparkles className="w-4 h-4 text-accent mt-0.5 shrink-0" />
              <span>
                <strong>Shark Tank Example:</strong> {item.example}
              </span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
