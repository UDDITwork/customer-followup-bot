#!/bin/bash

# Production Deployment Script for Google Cloud Run
# This script deploys the Customer Quote Request backend to Cloud Run

echo "================================"
echo "Production Deployment Script"
echo "================================"
echo ""

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo "❌ Error: gcloud CLI is not installed"
    echo "Install from: https://cloud.google.com/sdk/docs/install"
    exit 1
fi

echo "✅ gcloud CLI found"
echo ""

# Get project ID
read -p "Enter your Google Cloud Project ID: " PROJECT_ID

if [ -z "$PROJECT_ID" ]; then
    echo "❌ Error: Project ID is required"
    exit 1
fi

echo "📦 Setting project to: $PROJECT_ID"
gcloud config set project $PROJECT_ID

echo ""
echo "🚀 Deploying to Cloud Run..."
echo ""

gcloud run deploy customer-followup-api \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars ENVIRONMENT=production \
  --set-env-vars TURSO_DATABASE_URL=YOUR_TURSO_DATABASE_URL \
  --set-env-vars "TURSO_AUTH_TOKEN=YOUR_TURSO_AUTH_TOKEN" \
  --set-env-vars ANTHROPIC_API_KEY=YOUR_ANTHROPIC_API_KEY \
  --set-env-vars RESEND_API_KEY=YOUR_RESEND_API_KEY \
  --set-env-vars RESEND_FROM_EMAIL=YOUR_FROM_EMAIL \
  --set-env-vars FRONTEND_URL=http://localhost:5173 \
  --min-instances 0 \
  --max-instances 10 \
  --memory 512Mi \
  --cpu 1 \
  --timeout 300

echo ""
echo "================================"
echo "✅ Deployment Complete!"
echo "================================"
echo ""
echo "Next steps:"
echo "1. Copy the Service URL from above"
echo "2. Configure Resend webhook: https://resend.com/webhooks"
echo "   Webhook URL: https://your-service-url/webhooks/resend"
echo "   Event: email.received"
echo "3. Test by sending email to: newsletter@uddit.site"
echo ""
echo "View logs: gcloud run services logs read customer-followup-api --region us-central1"
echo ""
