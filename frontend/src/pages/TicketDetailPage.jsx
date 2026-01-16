import { useParams, Link } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { fetchTicketDetails } from '../services/api'
import { ArrowLeft } from 'lucide-react'
import { format } from 'date-fns'

const statusColors = {
  NEW: 'bg-blue-100 text-blue-800',
  WAITING_ON_CUSTOMER: 'bg-yellow-100 text-yellow-800',
  READY: 'bg-green-100 text-green-800',
}

function TicketDetailPage() {
  const { id } = useParams()

  const { data: ticket, isLoading } = useQuery({
    queryKey: ['ticket', id],
    queryFn: () => fetchTicketDetails(id),
  })

  if (isLoading) {
    return (
      <div className="max-w-5xl mx-auto px-4 py-8">
        <div className="text-center text-gray-500">Loading...</div>
      </div>
    )
  }

  if (!ticket) {
    return (
      <div className="max-w-5xl mx-auto px-4 py-8">
        <div className="text-center text-red-500">Ticket not found</div>
      </div>
    )
  }

  const missingFields = ticket.extracted_data?.laptop_model
    ? []
    : ['customer_name', 'laptop_model', 'ram', 'storage']

  return (
    <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Back button */}
      <Link
        to="/"
        className="inline-flex items-center gap-2 text-gray-600 hover:text-gray-900 mb-6"
      >
        <ArrowLeft size={20} />
        Back to Dashboard
      </Link>

      {/* Ticket Header */}
      <div className="bg-white rounded-lg shadow p-6 mb-6">
        <div className="flex items-start justify-between">
          <div>
            <p className="text-sm font-mono text-gray-500">
              {ticket.ticket_number}
            </p>
            <h1 className="text-2xl font-bold text-gray-900 mt-1">
              {ticket.customer_name || 'Unknown Customer'}
            </h1>
            <p className="text-gray-600 mt-1">{ticket.customer_email}</p>
          </div>
          <span
            className={`px-3 py-1 rounded-full text-sm font-medium ${
              statusColors[ticket.status]
            }`}
          >
            {ticket.status.replace(/_/g, ' ')}
          </span>
        </div>

        <div className="mt-4 flex gap-4 text-sm text-gray-500">
          <p>Created: {format(new Date(ticket.created_at), 'PPpp')}</p>
          <p>Updated: {format(new Date(ticket.updated_at), 'PPpp')}</p>
        </div>
      </div>

      {/* Extracted Data */}
      <div className="bg-white rounded-lg shadow p-6 mb-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">
          Quote Details
        </h2>

        {ticket.extracted_data ? (
          <div className="grid grid-cols-2 gap-4">
            <DataField label="Laptop Model" value={ticket.extracted_data.laptop_model} />
            <DataField label="RAM" value={ticket.extracted_data.ram} />
            <DataField label="Storage" value={ticket.extracted_data.storage} />
            <DataField label="Screen Size" value={ticket.extracted_data.screen_size} />
            <DataField label="Warranty" value={ticket.extracted_data.warranty} />
            <DataField label="Quantity" value={ticket.extracted_data.quantity} />
            <DataField
              label="Delivery Location"
              value={ticket.extracted_data.delivery_location}
              fullWidth
            />
            <DataField
              label="Delivery Timeline"
              value={ticket.extracted_data.delivery_timeline}
            />
            <DataField label="Budget" value={ticket.extracted_data.budget} />
          </div>
        ) : (
          <p className="text-gray-500">No extracted data available</p>
        )}
      </div>

      {/* Email Thread */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">
          Email Thread
        </h2>

        {ticket.email_threads && ticket.email_threads.length > 0 ? (
          <div className="space-y-4">
            {ticket.email_threads.map((email) => (
              <div
                key={email.id}
                className={`p-4 rounded-lg ${
                  email.direction === 'inbound'
                    ? 'bg-blue-50 border-l-4 border-blue-500'
                    : 'bg-gray-50 border-l-4 border-gray-400'
                }`}
              >
                <div className="flex items-center justify-between mb-2">
                  <span
                    className={`text-xs font-medium ${
                      email.direction === 'inbound'
                        ? 'text-blue-700'
                        : 'text-gray-700'
                    }`}
                  >
                    {email.direction === 'inbound' ? '📥 INBOUND' : '📤 OUTBOUND'}
                  </span>
                  <span className="text-xs text-gray-500">
                    {format(new Date(email.timestamp), 'PPpp')}
                  </span>
                </div>

                {email.email_subject && (
                  <p className="font-semibold text-gray-900 mb-2">
                    {email.email_subject}
                  </p>
                )}

                <p className="text-sm text-gray-700 whitespace-pre-wrap">
                  {email.email_body}
                </p>
              </div>
            ))}
          </div>
        ) : (
          <p className="text-gray-500">No emails in thread</p>
        )}
      </div>
    </div>
  )
}

function DataField({ label, value, fullWidth = false }) {
  return (
    <div className={fullWidth ? 'col-span-2' : ''}>
      <p className="text-sm font-medium text-gray-500">{label}</p>
      <p className="text-base text-gray-900 mt-1">
        {value || <span className="text-red-500">Missing</span>}
      </p>
    </div>
  )
}

export default TicketDetailPage
