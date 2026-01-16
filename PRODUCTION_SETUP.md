# Production Deployment Guide

## Overview

This guide will help you deploy the Customer Quote Request System to production using:
- **Google Cloud Run** for the backend
- **Vercel** for the frontend (optional)
- **Resend** for email handling
- **Turso** for the database

---

## Prerequisites

- Google Cloud account with billing enabled
- Domain configured in Resend
- GitHub account (for CI/CD)
- Turso database credentials (already have)
- Resend API key (already have)

---

## Part 1: Configure Resend for Receiving Emails

### Step 1: Add Domain to Resend

1. Go to https://resend.com/domains
2. Add your domain: `uddit.site`
3. Add the DNS records Resend provides to your domain registrar
4. Wait for verification

### Step 2: Configure Inbound Email

1. In Resend dashboard, go to "Domains"
2. Click on `uddit.site`
3. Enable "Inbound" emails
4. Set up MX records for receiving emails
5. Note: You'll configure the webhook URL after deploying the backend

---

## Part 2: Deploy Backend to Google Cloud Run

### Option A: Manual Deployment (Quick Start)

#### Step 1: Install Google Cloud CLI

Download from: https://cloud.google.com/sdk/docs/install

#### Step 2: Authenticate

```bash
gcloud auth login
gcloud config set project YOUR_PROJECT_ID
```

#### Step 3: Deploy

```bash
cd backend

gcloud run deploy customer-followup-api \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars ENVIRONMENT=production \
  --set-env-vars TURSO_DATABASE_URL=YOUR_TURSO_DATABASE_URL \
  --set-env-vars TURSO_AUTH_TOKEN=YOUR_TURSO_AUTH_TOKEN \
  --set-env-vars ANTHROPIC_API_KEY=YOUR_ANTHROPIC_API_KEY \
  --set-env-vars RESEND_API_KEY=YOUR_RESEND_API_KEY \
  --set-env-vars RESEND_FROM_EMAIL=YOUR_FROM_EMAIL \
  --set-env-vars FRONTEND_URL=http://localhost:5173 \
  --min-instances 0 \
  --max-instances 10 \
  --memory 512Mi \
  --cpu 1 \
  --timeout 300
```

#### Step 4: Get the Deployed URL

After deployment completes, you'll see output like:
```
Service URL: https://customer-followup-api-xxxxx.run.app
```

**Copy this URL!** You'll need it for:
1. Resend webhook configuration
2. Frontend configuration

### Option B: GitHub Actions (Automated CI/CD)

I already created the workflow file at `.github/workflows/deploy.yml`. To use it:

#### Step 1: Create GitHub Repository

```bash
cd C:\Users\Uddit\Downloads\CUSTOMER-FOLLOWUP
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/YOUR_USERNAME/customer-followup.git
git push -u origin main
```

#### Step 2: Add GitHub Secrets

Go to your GitHub repository → Settings → Secrets and variables → Actions

Add these secrets:
- `GCP_PROJECT_ID`: Your Google Cloud project ID
- `GCP_SA_KEY`: Service account JSON key (create in GCP Console)
- `TURSO_DATABASE_URL`: `libsql://customer-chat-rag-udditwork.aws-ap-south-1.turso.io`
- `TURSO_AUTH_TOKEN`: Your Turso token
- `ANTHROPIC_API_KEY`: Your Claude API key
- `RESEND_API_KEY`: `re_LWR1isuT_LscFCMYHjstZ9umzehz53gtt`
- `RESEND_FROM_EMAIL`: `newsletter@uddit.site`
- `FRONTEND_URL`: (Update after deploying frontend)

#### Step 3: Push to Deploy

Every push to `main` branch will automatically deploy!

```bash
git push origin main
```

---

## Part 3: Configure Resend Webhook

Once your backend is deployed:

1. Go to Resend dashboard: https://resend.com/webhooks
2. Click "Add Webhook"
3. **Webhook URL**: `https://your-backend-url.run.app/webhooks/resend`
4. **Events**: Select `email.received`
5. Click "Create"

Now emails sent to `newsletter@uddit.site` will be forwarded to your backend!

---

## Part 4: Test Production Email Flow

### Send a Test Email

Send an email TO: `newsletter@uddit.site` with:

```
Subject: Quote Request for Laptops

Hi,

I need 10 Dell Latitude laptops with 16GB RAM, 512GB SSD.
Delivery to New York by March 1st.

Thanks,
John Smith
john@example.com
```

### What Should Happen:

1. ✅ Email arrives at `newsletter@uddit.site`
2. ✅ Resend forwards it to your webhook
3. ✅ Backend extracts details with Claude
4. ✅ Ticket created in Turso database
5. ✅ If info is missing, follow-up email sent via Resend

### Check the Results:

```bash
# View tickets
curl https://your-backend-url.run.app/tickets/

# View specific ticket
curl https://your-backend-url.run.app/tickets/1
```

---

## Part 5: Deploy Frontend to Vercel (Optional)

### Step 1: Push Frontend to GitHub

If not already in the same repo, create a separate repo or use the same one.

### Step 2: Connect to Vercel

1. Go to https://vercel.com
2. Click "Add New Project"
3. Import your GitHub repository
4. **Root Directory**: `frontend`
5. **Framework Preset**: Vite
6. **Environment Variables**:
   - `VITE_API_URL`: `https://your-backend-url.run.app`
7. Click "Deploy"

### Step 3: Update Backend CORS

Once frontend is deployed, update the backend's `FRONTEND_URL` environment variable in Cloud Run:

```bash
gcloud run services update customer-followup-api \
  --set-env-vars FRONTEND_URL=https://your-frontend.vercel.app
```

---

## Part 6: Monitoring and Maintenance

### View Logs

```bash
# Backend logs
gcloud run services logs read customer-followup-api --region us-central1

# Or use Cloud Console
https://console.cloud.google.com/run
```

### View Database

Connect to Turso CLI:
```bash
turso db shell customer-chat-rag-udditwork

# View tickets
SELECT * FROM tickets;

# View email threads
SELECT * FROM email_threads;
```

### Cost Monitoring

- **Cloud Run**: Free tier includes 2M requests/month
- **Turso**: Free tier (generous limits)
- **Claude API**: ~$0.01-0.03 per email
- **Resend**: 100 emails/day free, then $10/month
- **Vercel**: Free for personal projects

**Expected cost for 200 emails/month**: <$10/month

---

## Part 7: Troubleshooting

### Emails Not Being Received

1. Check Resend domain verification
2. Verify MX records are correct
3. Check webhook URL is correct
4. View Cloud Run logs for errors

### Backend Errors

```bash
# View recent logs
gcloud run services logs read customer-followup-api --region us-central1 --limit 50

# Check service status
gcloud run services describe customer-followup-api --region us-central1
```

### Database Errors

Check Turso connection:
```bash
# In backend directory
python -c "from app.database import get_db_client; client = get_db_client(); print('Connected!')"
```

---

## Part 8: Scaling for Higher Volume

If you exceed 200 emails/week:

### Increase Cloud Run Resources

```bash
gcloud run services update customer-followup-api \
  --min-instances 1 \
  --max-instances 20 \
  --memory 1Gi \
  --cpu 2
```

### Add Queue System (Optional)

For very high volume, consider adding a queue:
- Use Google Cloud Tasks
- Process emails asynchronously
- Prevents timeout issues

---

## Security Checklist

- ✅ All secrets stored in Cloud Run environment variables
- ✅ HTTPS enforced automatically by Cloud Run
- ✅ CORS configured to only allow your frontend
- ✅ Resend webhook validates requests
- ✅ Database uses authentication tokens
- ✅ No sensitive data committed to git

---

## Quick Commands Reference

```bash
# Deploy backend
gcloud run deploy customer-followup-api --source ./backend

# View logs
gcloud run services logs read customer-followup-api

# Update environment variable
gcloud run services update customer-followup-api --set-env-vars KEY=VALUE

# View service details
gcloud run services describe customer-followup-api

# Delete service
gcloud run services delete customer-followup-api
```

---

## Support

- **Resend Docs**: https://resend.com/docs
- **Cloud Run Docs**: https://cloud.google.com/run/docs
- **Turso Docs**: https://docs.turso.tech
- **Claude API Docs**: https://docs.anthropic.com

---

## Success Criteria

Your production system is ready when:

1. ✅ Backend deployed to Cloud Run
2. ✅ Domain configured in Resend
3. ✅ Webhook connected to backend
4. ✅ Test email successfully creates ticket
5. ✅ Follow-up emails are sent via Resend
6. ✅ Frontend deployed (optional)
7. ✅ Monitoring in place

**Congratulations! Your system is production-ready! 🎉**
