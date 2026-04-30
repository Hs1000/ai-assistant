"""Run once to generate all PDF reports into data/pdfs/"""
import os
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors

OUT = os.path.join(os.path.dirname(__file__), "pdfs")
os.makedirs(OUT, exist_ok=True)

styles = getSampleStyleSheet()
H1 = ParagraphStyle("h1", parent=styles["Heading1"], fontSize=16, spaceAfter=10)
H2 = ParagraphStyle("h2", parent=styles["Heading2"], fontSize=13, spaceAfter=6)
BODY = styles["BodyText"]
BODY.spaceAfter = 8


def build(filename, title, sections):
    path = os.path.join(OUT, filename)
    doc = SimpleDocTemplate(path, pagesize=letter,
                            leftMargin=inch, rightMargin=inch,
                            topMargin=inch, bottomMargin=inch)
    story = [Paragraph(title, H1), Spacer(1, 0.2 * inch)]
    for heading, paragraphs in sections:
        story.append(Paragraph(heading, H2))
        for p in paragraphs:
            story.append(Paragraph(p, BODY))
        story.append(Spacer(1, 0.15 * inch))
    doc.build(story)
    print(f"Created: {path}")


# ── 1. Quarterly Executive Report ────────────────────────────────────────────
build("quarterly_executive_report.pdf", "Quarterly Executive Report – Q1 2025", [
    ("Executive Summary", [
        "Q1 2025 was a landmark quarter for our streaming platform. Total viewership surged by 34% year-over-year, driven by blockbuster releases in the Action and Sci-Fi categories. Revenue reached $1.2B, exceeding the quarterly target by 18%.",
        "Stellar Run became the fastest-growing title in platform history, accumulating over 4.2 million views within 30 days of release. Hollow Earth, released in April, is already tracking above forecast.",
    ]),
    ("Title Performance", [
        "Top performing titles in Q1 2025: Stellar Run (8.7 rating, 4.2M views), Fire & Frost (8.5 rating, 4.6M views), Vortex Rising (8.8 rating, 4.9M views).",
        "Comedy titles continued to underperform. The Laughing House and Laugh Track both registered below-average completion rates (under 50%) and sentiment scores in the negative range. Comedy genre average rating dropped to 5.5, the lowest of all genres.",
        "Drama titles showed steady growth, with Last Kingdom and Broken Compass maintaining strong audience retention above 85%.",
    ]),
    ("Regional Highlights", [
        "Mumbai led all cities with 610,000 views in March 2025 and an engagement score of 83. New York followed with 520,000 views and the highest engagement score of 88.",
        "London showed exceptional growth, ranking third globally with 430,000 views. The UK market overall grew 28% quarter-over-quarter.",
        "Emerging markets including Lagos and Nairobi showed growing audiences but with below-average watch times, suggesting content localization opportunities.",
    ]),
    ("Financial Summary", [
        "Marketing spend was highest for Hollow Earth ($1.2M across all channels) followed by Fire & Frost ($890K). Return on ad spend (ROAS) was strongest for Social Media and Influencer channels.",
        "Premium subscriptions grew 22% QoQ. Standard and Basic tiers showed flat growth, indicating an opportunity to convert mid-tier users.",
    ]),
    ("Leadership Recommendations", [
        "Invest further in Action and Sci-Fi production to capitalize on their dominant performance metrics.",
        "Conduct a strategic review of the Comedy vertical. Consider bringing in new creative talent and refreshing the content formula, as current comedy titles are underperforming on all key metrics including rating, completion rate, and sentiment.",
        "Expand localized content for high-growth markets in South Asia and the Middle East.",
        "Increase influencer marketing budget by 30% given its superior conversion rates compared to traditional TV advertising.",
        "Launch a Premium tier loyalty program to reduce churn among high-value subscribers.",
    ]),
])

# ── 2. Campaign Performance Summary ─────────────────────────────────────────
build("campaign_performance_summary.pdf", "Campaign Performance Summary – 2024/2025", [
    ("Overview", [
        "This report summarizes marketing campaign results across all titles and channels for fiscal year 2024-2025. Total marketing investment was $12.4M generating 285M impressions and 8.9M conversions.",
        "Social Media and Influencer campaigns consistently outperformed TV Ads in cost-per-conversion metrics.",
    ]),
    ("Top Performing Campaigns", [
        "Hollow Earth – Social Media campaign achieved 510,000 conversions on $320K spend (ROAS: 4.8x). The Influencer campaign delivered 124,000 conversions with a 540,000 click volume.",
        "Stellar Run – All four channels (Social Media, TV, Search, Influencer) delivered above-benchmark results. The Influencer campaign achieved an 88,000 conversion rate at the lowest cost-per-click.",
        "Fire & Frost – Social Media drove 470,000 clicks and 106,000 conversions. The title's strong organic buzz amplified paid campaign results.",
    ]),
    ("Underperforming Campaigns", [
        "Comedy titles showed consistently weak campaign results. The Laughing House generated only 12,000 conversions on $80K Social Media spend. Laugh Track and The Comedy Club similarly underdelivered.",
        "TV Ads for comedy content had especially poor performance, with high CPM but low conversion rates, suggesting comedy audiences are less responsive to traditional broadcast advertising.",
    ]),
    ("Channel Analysis", [
        "Social Media: Best overall channel, averaging 62,000 conversions per campaign at lowest cost.",
        "Influencer: Second best channel, particularly effective for Action and Sci-Fi titles. Average 97,000 conversions per campaign.",
        "TV Ads: Highest reach but lowest conversion efficiency. Best suited for broad awareness campaigns for blockbuster releases.",
        "Search Ads: Effective for targeted audiences already interested in specific genres. Best ROI for Drama titles.",
    ]),
    ("Recommendations", [
        "Shift 15-20% of TV Ad budget to Influencer campaigns for 2025-2026.",
        "Develop a comedy-specific campaign strategy with audience testing before major launches.",
        "Increase Search Ad budgets for Drama titles where intent-based targeting is most effective.",
    ]),
])

# ── 3. Content Roadmap ───────────────────────────────────────────────────────
build("content_roadmap.pdf", "Content Roadmap – 2025/2026", [
    ("Strategic Vision", [
        "Our content roadmap for 2025-2026 focuses on three pillars: expanding our Action and Sci-Fi slate to meet demonstrated demand, revitalizing the Comedy vertical with fresh talent, and growing original Drama productions for underserved markets.",
    ]),
    ("Q2–Q3 2025 Releases", [
        "Vortex Rising (Sci-Fi) – Already released June 2025, tracking at 4.9M views and climbing. Sequel greenlit.",
        "Silent Echo (Thriller) – August 2025 release. Pre-release buzz is strong. Marketing campaign focuses on mystery and suspense angles.",
        "Blue Horizon (Drama) – July 2025. Family drama targeting suburban demographics. Influencer campaign with family lifestyle creators.",
    ]),
    ("Q4 2025 Pipeline", [
        "Stellar Run 2 (Action) – Sequel to the highest-rated title of 2025. Production budget: $120M. Release target: November 2025.",
        "Cosmic Drift (Sci-Fi) – Original IP with strong concept test scores. Budget: $150M. Targeting the same demographic as Hollow Earth.",
        "Comedy Reboot Initiative – Three new comedy series with reformed creative direction, based on audience research indicating preference for character-driven, observational humor over slapstick.",
    ]),
    ("2026 Strategic Slate", [
        "At least 6 original Action titles planned, maintaining genre leadership.",
        "2 prestige Drama productions targeting award recognition and long-tail viewership.",
        "International co-productions for Mumbai, London, and Dubai markets to capitalize on strong regional engagement.",
        "Comedy vertical target: achieve genre average rating of 7.0+ by Q4 2026 through new talent and format experimentation.",
    ]),
    ("Trending Content Signals", [
        "Stellar Run is trending due to its unique blend of high-octane action sequences, a critically praised screenplay, and strong word-of-mouth amplified by social media discussions. The title topped trending charts for 6 consecutive weeks.",
        "Hollow Earth is trending due to its groundbreaking visual effects and a thought-provoking storyline that generated significant online discourse.",
    ]),
])

# ── 4. Policy Guidelines ─────────────────────────────────────────────────────
build("policy_guidelines.pdf", "Content & Data Policy Guidelines", [
    ("Content Classification Policy", [
        "All titles must be classified by genre, rating, and audience suitability before release. Misclassification may result in campaign inefficiencies and audience mismatch.",
        "Action, Sci-Fi, and Thriller titles require age-gating for audiences under 13. Drama and Comedy titles require content advisories where applicable.",
    ]),
    ("Data Collection & Privacy", [
        "Watch activity data is collected with explicit user consent. Viewer IDs are anonymized in all analytics exports. Personal data is never shared with third-party advertisers.",
        "Regional performance data is aggregated at the city level to prevent individual identification. Minimum cohort size for any reported metric is 1,000 viewers.",
    ]),
    ("Marketing Spend Governance", [
        "All campaigns above $100K require senior marketing approval. Campaigns above $500K require executive sign-off.",
        "Influencer partnerships must be disclosed per FTC guidelines. All sponsored content must include #ad or #sponsored tags.",
        "Channel budget allocations must be reviewed quarterly against conversion benchmarks.",
    ]),
    ("Review & Rating Standards", [
        "Viewer reviews are monitored for authenticity. Reviews from accounts with suspicious activity patterns are quarantined pending review.",
        "Sentiment analysis is performed on all reviews. Titles with negative sentiment scores below -0.3 trigger an automatic content quality review.",
        "Star ratings below 4/10 from more than 20% of reviewers triggers a leadership review of the content acquisition decision.",
    ]),
    ("Compliance & Reporting", [
        "Quarterly performance reports must be submitted to the board within 30 days of quarter end.",
        "Regional performance data must be reviewed monthly by regional leads with escalation protocols for engagement score drops exceeding 15%.",
    ]),
])

# ── 5. Audience Behavior Report ──────────────────────────────────────────────
build("audience_behavior_report.pdf", "Audience Behavior Report – Q1 2025", [
    ("Viewing Patterns", [
        "Average watch time across all titles was 87 minutes in Q1 2025, up from 79 minutes in Q1 2024. Action genre leads with 106 minutes average, followed by Sci-Fi at 98 minutes.",
        "Completion rates are highest for Action (93%) and Sci-Fi (90%) titles. Comedy titles average only 38% completion rate, indicating significant audience drop-off.",
        "Mobile is the fastest-growing device, accounting for 42% of all views. TV remains dominant at 48%. Laptop accounts for 10%.",
    ]),
    ("Demographics", [
        "Core audience aged 25-44 accounts for 61% of total viewership. The 18-24 segment is growing fastest at 28% YoY.",
        "Gender split is 54% male, 46% female. Female viewers show stronger preference for Drama titles; male viewers skew toward Action and Sci-Fi.",
        "Premium subscribers watch 2.3x more content than Basic subscribers and have 94% higher completion rates.",
    ]),
    ("Engagement Analysis", [
        "Mumbai has the highest engagement score globally at 83, driven by large youth population and high smartphone penetration. New York leads among Western markets at 88.",
        "Engagement scores correlate strongly with content quality ratings. Titles rated above 8.0 average an engagement score 40% higher than titles below 7.0.",
        "Comedy titles show the weakest engagement, with The Laughing House, Laugh Track, and The Comedy Club all scoring below 35 on the engagement index.",
    ]),
    ("Binge Behavior", [
        "Action and Sci-Fi viewers are most likely to rewatch titles or watch sequels. 28% of Stellar Run viewers started watching the movie a second time within 7 days.",
        "Drama viewers have the highest cross-title discovery rate: after watching Last Kingdom, 67% went on to watch at least one other Drama title within 30 days.",
    ]),
    ("Comedy Performance Analysis", [
        "Comedy genre weak performance is explained by several factors: outdated humor formats, low production values relative to audience expectations, and poor demographic targeting in marketing campaigns.",
        "Audience research indicates that the comedy content currently available appeals to a narrower demographic than intended. The 18-24 age group, which drives most viral content sharing, is underserved by current comedy offerings.",
        "Recommendations to improve comedy: refresh creative direction, invest in character-driven scripts, improve casting with talent that resonates with younger demographics, and pilot shorter-format comedy content.",
    ]),
])

print("All PDFs generated successfully.")
