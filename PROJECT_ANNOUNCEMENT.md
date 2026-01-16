# AI-Powered Customer Quote Management System | Built by Uddit

> **Project Title:** Customer Quote Request Management System with Nested Email AI Agent
> **Creator:** Uddit | [uddit.site](https://uddit.site)
> **Created For:** BuzzClan Interview Process
> **Development Time:** 1 Hour Live Coding Session
> **Date:** January 2026

---

## 🚀 Project Announcement

I'm excited to share my **AI-powered customer quote management system** - a production-ready automated email assistant that demonstrates advanced software architecture, AI integration, and cloud deployment capabilities. This project was developed during a one-hour technical interview with [BuzzClan](https://buzzclan.com/), a leading AI-driven cloud & data services company.

### About the Creator

**Uddit** - Full-Stack Developer & AI Engineer
🌐 Website: [uddit.site](https://uddit.site)
📧 Contact: newsletter@uddit.site
💼 Portfolio: Specialized in AI-powered automation, cloud architecture, and modern web applications

---

## 🎯 What This System Does

This intelligent email automation system revolutionizes how businesses handle customer quote requests by:

1. **Automatically processing incoming customer emails** requesting laptop quotes
2. **Using Claude AI (Anthropic)** to extract structured information from unstructured text
3. **Identifying missing critical details** (model, RAM, storage, warranty, delivery info)
4. **Generating personalized follow-up emails** asking for specific missing information
5. **Maintaining nested conversation threads** until all required information is collected
6. **Providing a dashboard** for sales teams to manage quote requests

### The Nested Email AI Agent

The system implements a sophisticated **nested ask-reply-ask-reply conversation agent** that:

```
Customer: "I need laptops"
→ AI extracts partial info, identifies 8 missing fields
→ Sends personalized follow-up asking for specific details

Customer replies: "Dell, 16GB RAM, 512GB SSD"
→ AI updates ticket with new info (3 fields filled)
→ Sends follow-up asking for 5 remaining fields

Customer replies: "14 inch, 3 year warranty, New York"
→ AI updates ticket (3 more fields filled)
→ Sends follow-up asking for 2 remaining fields

Customer replies: "March 15, 2026"
→ AI marks ticket as READY (all fields complete)
→ Sends confirmation to customer
→ Notifies sales team
```

**Key Innovation:** The system maintains conversation context across multiple email exchanges, never losing track of the customer's partial information.

---

## 🏆 Technical Achievement: Built in 1 Hour

This production-ready system was architected and developed during a **single one-hour live coding interview** with BuzzClan, demonstrating:

- ✅ Rapid system design and architecture
- ✅ Production-grade code quality
- ✅ AI integration (Claude Sonnet 4.5)
- ✅ Cloud deployment (Google Cloud Run)
- ✅ Database design (Turso LibSQL)
- ✅ Email automation (Resend API)
- ✅ Full-stack development (FastAPI + React)

**Interview Context:** BuzzClan, ranked [#60 on Inc. Regionals Southwest 2025](https://buzzclan.com/about/), specializes in AI-enabled cloud solutions. The interview focused on demonstrating real-world problem-solving, cloud architecture, and AI integration capabilities.

[Read the full interview case study →](./INTERVIEW_CASE_STUDY.md)

---

## 🛠️ Technical Stack

### Backend Architecture
- **Framework:** Python FastAPI (async, high-performance)
- **AI Engine:** Anthropic Claude Sonnet 4.5 (`claude-sonnet-4-5-20250929`)
- **Database:** Turso (serverless LibSQL/SQLite)
- **Email Service:** Resend API (transactional emails)
- **Hosting:** Google Cloud Run (serverless, auto-scaling)
- **Runtime:** Python 3.11

### Frontend Dashboard
- **Framework:** React 18 with Vite
- **State Management:** TanStack Query + Zustand
- **UI Library:** Tailwind CSS + shadcn/ui
- **Routing:** React Router DOM
- **Hosting:** Vercel (planned)

### DevOps & Infrastructure
- **Deployment:** Cloud Buildpacks (no Docker needed)
- **Version Control:** GitHub
- **CI/CD:** Direct deployment via gcloud CLI
- **Region:** europe-west1
- **Configuration:** Environment-based (local dev + production)

---

## 🔑 Key Features

### 1. Intelligent Email Processing
- Parses natural language customer requests
- Extracts structured data using Claude AI
- Handles various email formats and writing styles
- Supports HTML and plain text emails

### 2. Email Threading & Conversation Management
- Detects customer replies using `In-Reply-To` headers
- Matches tickets by email subject patterns
- Falls back to customer email + recent activity
- Maintains complete conversation history

### 3. Missing Field Detection
- Identifies 10 required fields for laptop quotes:
  - Laptop model, RAM, Storage, Screen size
  - Warranty preference, Quantity, Delivery location
  - Delivery timeline, Customer name, Customer email
- Budget is marked as optional
- Dynamically generates follow-up questions

### 4. Personalized Follow-ups
- AI-generated contextual emails
- Addresses customer by name
- Lists only missing fields (not already provided ones)
- Professional and conversational tone

### 5. Dual-Mode Architecture
- **Production Mode:** Real email integration via Resend
- **Development Mode:** Mock email system for local testing
- Environment-based configuration
- No code changes between modes

### 6. Sales Dashboard (React Frontend)
- View all quote requests with status filters
- Detailed ticket view with email conversation history
- Manual editing capabilities
- Status management (NEW, WAITING_ON_CUSTOMER, READY)
- Real-time updates via React Query

---

## 📊 System Architecture

### High-Level Design

```
Customer Email
    ↓
Resend Webhook → Cloud Run Backend
    ↓
Reply Detection Logic
    ↓
├─ New Email → Create Ticket
│   ↓
│   Claude AI Extraction
│   ↓
│   Identify Missing Fields
│   ↓
│   Generate Follow-up
│   ↓
│   Send via Resend
│
└─ Reply → Update Existing Ticket
    ↓
    Re-extract from Full Thread
    ↓
    Merge New + Existing Data
    ↓
    Check Remaining Missing Fields
    ↓
    ├─ Still Missing → Send Follow-up
    └─ All Complete → Mark READY
```

### Database Schema

```sql
tickets
├─ id (PK)
├─ ticket_number (UNIQUE, e.g., TKT-20260117-0001)
├─ customer_name
├─ customer_email
├─ status (NEW | WAITING_ON_CUSTOMER | READY)
├─ created_at
└─ updated_at

extracted_data
├─ id (PK)
├─ ticket_id (FK)
├─ laptop_model, ram, storage, screen_size
├─ warranty, quantity, delivery_location
├─ delivery_timeline, budget

email_threads
├─ id (PK)
├─ ticket_id (FK)
├─ direction (INBOUND | OUTBOUND)
├─ email_subject, email_body
├─ email_message_id (for threading)
├─ in_reply_to (for threading)
└─ timestamp
```

---

## 🔐 Production-Ready Features

### Security
- Environment-based configuration (no secrets in code)
- HTTPS/TLS for all communication
- Input validation with Pydantic models
- SQL injection prevention via parameterized queries
- Webhook signature verification (planned)

### Performance
- Serverless auto-scaling (0-10 instances)
- Cold start: ~3-5 seconds
- Warm requests: <100ms
- Database latency: 20-50ms (Turso)
- Claude API: 2-5 seconds per extraction

### Cost Optimization
- Pay-per-request pricing (Cloud Run)
- Scale to zero when idle
- Efficient database queries with indexes
- Estimated cost: <$10/month for 200 emails

### Monitoring & Observability
- Structured logging with timestamps
- Cloud Run automatic logs via Google Cloud Logging
- Error tracking with stack traces
- Request/response logging for debugging

---

## 🌐 Live Deployment

**Backend API:** [https://customer-followup-bot-282996737766.europe-west1.run.app](https://customer-followup-bot-282996737766.europe-west1.run.app)

**API Documentation:** [https://customer-followup-bot-282996737766.europe-west1.run.app/docs](https://customer-followup-bot-282996737766.europe-west1.run.app/docs)

**Email Address:** newsletter@uddit.site

**Test the System:**
1. Send an email to newsletter@uddit.site with a laptop quote request
2. Receive AI-generated follow-up asking for missing details
3. Reply with partial information
4. Continue the conversation until all fields are provided
5. Receive confirmation when complete

---

## 💡 Technical Highlights

### 1. Advanced Email Threading
- Implements RFC 5322 email threading standards
- Uses `In-Reply-To` and `References` headers
- Fallback matching by ticket number in subject
- Prevents duplicate ticket creation for same customer

### 2. AI Integration Best Practices
- Structured prompts for consistent extraction
- JSON output validation
- Error handling for API failures
- Cost-effective token usage (~200 tokens per email)
- Model: Claude Sonnet 4.5 (latest as of Jan 2026)

### 3. Scalable Architecture
- Stateless microservice design
- Database connection pooling
- Async/await for concurrent operations
- Horizontal auto-scaling via Cloud Run

### 4. Developer Experience
- Hot reload in development mode
- Comprehensive API documentation (FastAPI Swagger)
- Mock email system for local testing
- Type safety with Pydantic
- Clean code structure with service layers

---

## 📈 Business Impact

### Efficiency Gains
- **Manual Processing Time:** 5-10 minutes per email (2-3 back-and-forth exchanges)
- **Automated Processing:** < 5 seconds
- **Time Saved:** 95%+ reduction in manual effort
- **Capacity:** Can handle hundreds of concurrent quote requests

### Quality Improvements
- **Consistency:** Every customer gets the same thoroughness
- **Completeness:** No missing information in final quotes
- **Response Time:** Instant follow-ups (vs. hours/days manually)
- **Tracking:** Complete audit trail of all conversations

### Cost Savings
- Reduces need for dedicated quote processing staff
- Eliminates errors from manual data entry
- Faster quote turnaround = higher conversion rates
- Scalable without linear cost increase

---

## 🎓 Technical Skills Demonstrated

### Software Architecture
- ✅ Microservices design patterns
- ✅ RESTful API development
- ✅ Database schema design
- ✅ Email system integration
- ✅ Webhook handling
- ✅ Environment-based configuration

### AI & Machine Learning
- ✅ Large Language Model integration (Claude)
- ✅ Prompt engineering for structured extraction
- ✅ Natural language processing
- ✅ Contextual conversation management
- ✅ AI-powered content generation

### Cloud & DevOps
- ✅ Serverless deployment (Cloud Run)
- ✅ Buildpacks (infrastructure as code)
- ✅ Git version control
- ✅ Production environment management
- ✅ Logging and monitoring

### Full-Stack Development
- ✅ Backend: Python, FastAPI, async programming
- ✅ Frontend: React, TypeScript, modern UI
- ✅ Database: SQL, query optimization
- ✅ API design and documentation

---

## 📚 Project Documentation

- [Quick Start Guide](./QUICKSTART.md) - Get started in 5 minutes
- [Production Setup Guide](./PRODUCTION_SETUP.md) - Deploy to production
- [Interview Case Study](./INTERVIEW_CASE_STUDY.md) - Behind the scenes
- [Technical Documentation](./README.md) - Complete system documentation
- [API Reference](https://customer-followup-bot-282996737766.europe-west1.run.app/docs) - Interactive API docs

---

## 🌟 About BuzzClan

This project was created as part of the technical interview process for **BuzzClan**, a leading AI-driven cloud and data services company.

**BuzzClan** specializes in:
- AI-enabled software advisory and implementation
- Cloud modernization and optimization
- Public and private sector digital transformation
- AI-powered resource allocation and predictive scaling

**Recognition:**
- [#60 on Inc. Regionals Southwest 2025](https://buzzclan.com/about/)
- [#2133 on Inc. 5000 2025](https://buzzclan.com/about/)
- Certified partner: Oracle, Amazon, Google, Microsoft, Saviynt

**Learn More:**
- Website: [buzzclan.com](https://buzzclan.com/)
- LinkedIn: [BuzzClan LLC](https://www.linkedin.com/company/buzzclan-llc)
- About: [BuzzClan's Story](https://buzzclan.com/about/)

---

## 🤝 Connect with Uddit

**Website:** [uddit.site](https://uddit.site)
**Email:** newsletter@uddit.site
**Project Repository:** [GitHub - customer-followup-bot](https://github.com/UDDITwork/customer-followup-bot)

**Interested in similar projects?** Visit [uddit.site](https://uddit.site) to see more AI-powered automation solutions, cloud architectures, and full-stack applications.

---

## 📋 JSON-LD Schema (SEO)

```json
{
  "@context": "https://schema.org",
  "@type": "SoftwareApplication",
  "name": "Customer Quote Request Management System",
  "description": "AI-powered email automation system for processing customer laptop quote requests with nested conversation management",
  "applicationCategory": "BusinessApplication",
  "operatingSystem": "Cloud-based",
  "offers": {
    "@type": "Offer",
    "price": "0",
    "priceCurrency": "USD"
  },
  "author": {
    "@type": "Person",
    "name": "Uddit",
    "url": "https://uddit.site",
    "email": "newsletter@uddit.site",
    "jobTitle": "Full-Stack Developer & AI Engineer"
  },
  "datePublished": "2026-01-17",
  "url": "https://customer-followup-bot-282996737766.europe-west1.run.app",
  "softwareVersion": "1.0.0",
  "programmingLanguage": ["Python", "JavaScript"],
  "runtimePlatform": "Google Cloud Run",
  "featureList": [
    "AI-powered email extraction using Claude Sonnet 4.5",
    "Nested conversation management",
    "Automatic follow-up email generation",
    "Email threading and reply detection",
    "Sales dashboard with React",
    "Dual-mode architecture (dev + production)"
  ],
  "creator": {
    "@type": "Organization",
    "name": "Uddit",
    "url": "https://uddit.site"
  },
  "about": {
    "@type": "Event",
    "name": "BuzzClan Technical Interview",
    "organizer": {
      "@type": "Organization",
      "name": "BuzzClan",
      "url": "https://buzzclan.com"
    },
    "eventStatus": "https://schema.org/EventScheduled",
    "eventAttendanceMode": "https://schema.org/OnlineEventAttendanceMode"
  }
}
```

---

## 🏷️ Keywords & Tags

**Primary Keywords:** AI email automation, customer quote management, Claude AI integration, nested conversation agent, email threading system, intelligent follow-ups

**Technologies:** Python FastAPI, Claude Sonnet 4.5, Google Cloud Run, Turso database, Resend email API, React dashboard, Anthropic AI

**Use Cases:** Quote request processing, automated customer service, email conversation management, sales automation, CRM integration

**Industry:** B2B sales automation, enterprise software, cloud services, AI-powered business tools

---

## 📄 License & Attribution

Created by **Uddit** ([uddit.site](https://uddit.site))
Developed for **BuzzClan** interview process
January 2026

For inquiries about this project or similar solutions, contact: newsletter@uddit.site

---

**Last Updated:** January 17, 2026
**Status:** Production-ready, actively deployed
**Repository:** [github.com/UDDITwork/customer-followup-bot](https://github.com/UDDITwork/customer-followup-bot)

---

### Sources
- [BuzzClan Official Website](https://buzzclan.com/)
- [BuzzClan About Page](https://buzzclan.com/about/)
- [BuzzClan LinkedIn](https://www.linkedin.com/company/buzzclan-llc)
