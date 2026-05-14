# Affiliate Marketing Platform

A modern, enterprise-grade affiliate marketing system built with .NET 8, featuring real-time tracking, fraud prevention, and comprehensive analytics.

## Project Overview

### Affiliate Role
Affiliates can generate unique referral links, track their performance through detailed dashboards, and earn commissions on successful conversions. The system provides comprehensive analytics including click tracking, geographic insights, and revenue reporting.

### Support/Admin Role
Administrators have full system oversight with capabilities to manage global commission rates, monitor audit logs for fraud investigation, and access global analytics dashboards. The admin panel provides top-level insights into product performance, geographic distribution, and overall system health.

## File Structure

```
AffiliateMarketing/
├── Affiliate.Events/
│   └── AffiliateEvents.cs
├── AffiliateMarketing.API/
│   ├── Controllers/
│   │   ├── AdminManagementController.cs
│   │   ├── AffiliateDashboardController.cs
│   │   ├── ClickTrackingController.cs
│   │   ├── DashboardContoller.cs
│   │   ├── ReferralLinksController.cs
│   │   └── UserProvisioningController.cs
│   └── Program.cs
├── AffiliateMarketing.Application/
│   ├── Common/
│   │   ├── Behaviours/
│   │   │   └── ValidationBehaviour.cs
│   │   ├── DTOs/
│   │   │   └── ValidationResultDto.cs
│   │   └── Interfaces/
│   │       ├── IAffiliateDbContext.cs
│   │       ├── ICurrentUserService.cs
│   │       ├── IDateTime.cs
│   │       ├── IGeoLocationService.cs
│   │       ├── ILogService.cs
│   │       ├── IMessageProducer.cs
│   │       ├── IProductRepository.cs
│   │       ├── IProductService.cs
│   │       ├── ISchemaDiscoveryService.cs
│   │       ├── ITrackingRepository.cs
│   │       └── IUserRepository.cs
│   └── Features/
│       ├── Affiliates/
│       │   ├── Commands/
│       │   │   ├── GenerateLinkCommand.cs
│       │   │   ├── GenerateLinkHandler.cs
│       │   │   ├── RegisterAffiliateCommand.cs
│       │   │   └── RegisterAffiliateHandler.cs
│       │   └── Queries/
│       │       └── GetAffiliateDashboardQuery.cs
│       ├── Dashboard/
│       │   ├── Commands/
│       │   │   └── SimulateSaleCommand.cs
│       │   ├── DTOs/
│       │   │   └── DashboardSummaryDto.cs
│       │   └── Handlers/
│       │       ├── GetDashboardSummaryHandler.cs
│       │       └── SimulateSaleHandler.cs
│       ├── Products/
│       │   ├── Commands/
│       │   │   ├── CreateProductCommand.cs
│       │   │   ├── CreateProductHandler.cs
│       │   │   ├── SetCommissionCommand.cs
│       │   │   └── SetCommissionHandler.cs
│       │   └── Queries/
│       │       └── GetProductStatsQuery.cs
│       ├── Referrals/
│       │   ├── Commands/
│       │   │   ├── ValidateReferralCommand.cs
│       │   │   └── ValidateReferralHandler.cs
│       │   └── Queries/
│       │       └── GetReferralStatsQuery.cs
│       └── Tracking/
│           ├── Commands/
│           │   ├── RecordClickCommand.cs
│           │   └── RecordClickHandler.cs
│           └── Queries/
│               └── GetTrackingStatsQuery.cs
├── AffiliateMarketing.Contracts/
│   ├── Affiliate/
│   │   ├── AffiliateMetricsResponse.cs
│   │   └── AffiliateProductResponse.cs
│   ├── Identity/
│   │   ├── RegisterUserRequest.cs
│   │   └── RegisterUserRequestValidator.cs
│   └── Products/
│       ├── CreateProductRequest.cs
│       ├── CreateProductRequestValidator.cs
│       ├── SetCommissionRequest.cs
│       └── SetCommissionRequestValidator.cs
├── AffiliateMarketing.Domain/
│   ├── Entities/
│   │   ├── AffiliateProfile.cs
│   │   ├── AuditLog.cs
│   │   ├── ClickEvent.cs
│   │   ├── Conversion.cs
│   │   ├── Product.cs
│   │   └── ReferralLink.cs
│   ├── Enums/
│   │   ├── CommissionType.cs
│   │   └── ReferralStatus.cs
│   └── Events/
│       └── DomainEvents.cs
└── AffiliateMarketing.Infrastructure/
    ├── Data/
    │   ├── AffiliateDbContext.cs
    │   └── Migrations/
    ├── Logging/
    │   └── KafkaLogService.cs
    ├── Messaging/
    │   ├── Handlers/
    │   │   └── AffiliateKafkaHandler.cs
    │   └── KafkaProducerService.cs
    ├── Services/
    │   ├── GeoLocationService.cs
    │   └── ProductRepository.cs
    └── Tracking/
        └── TrackingRepository.cs
```

## The 'Product Story' Flow

### Click Journey: From ClickTrackingController to Database and Kafka

1. **Initial Click Capture**
   - User clicks a referral link: `GET /api/v1/r/{code}`
   - `ClickTrackingController.RedirectAndTrack()` captures raw metadata including IP address, user agent, and platform (UTM source)

2. **Command Processing**
   - Controller creates `RecordClickCommand` with captured data
   - Command is sent to `RecordClickHandler` via MediatR

3. **Enhanced Data Enrichment**
   - Handler fetches referral link and product details from database
   - Real-time geo-location data is retrieved using `IGeoLocationService` (IpInfo integration)
   - Enhanced `ClickEvent` entity is created with:
     - Geographic data (Country, City, Region)
     - Product association
     - Complete tracking metadata

4. **Database Persistence**
   - Click event is saved to PostgreSQL database
   - Includes high-resolution geo data for dashboard analytics

5. **Kafka Integration**
   - All significant actions are logged to Kafka via `KafkaLogService`
   - Audit trail includes user actions, system events, and security alerts
   - Messages are published to `affiliate-logs` topic for centralized monitoring

6. **User Redirect**
   - User is redirected to product page with referral parameter
   - Fallback to main site if referral code is invalid

## API Features Overview

### User Provisioning & Identity Sync
POST /affiliate/api/v1/users/sync

**What It Does:**

Registers a new user as an affiliate in the system and creates their affiliate profile.

**Access Control:**

Public endpoint for external Auth API integration. No authentication required for Phase 1.

**Request:**

POST /affiliate/api/v1/users/sync

```json
{
  "username": "john_doe",
  "email": "john@example.com",
  "password": "SecurePassword123"
}
```

**Sample Response:**

201 Created

```json
"550e8400-e29b-41d4-a716-446655440000"
```

**How It Works:**

The backend receives user data from the external Auth API, creates an affiliate profile with a unique TrackingId, and logs the action for security auditing.

### Affiliate Dashboard Access
GET /affiliate/api/v1/dashboard/summary

**What It Does:**

Returns comprehensive performance analytics for the logged-in affiliate including clicks, conversions, and revenue metrics.

**Access Control:**

Affiliates only (authentication temporarily disabled for Phase 1 demo).

**Request:**

GET /affiliate/api/v1/dashboard/summary

Authorization: Bearer <JWT>

**Sample Response:**

```json
{
  "totalClicks": 1250,
  "totalConversions": 45,
  "totalRevenue": 2250.00,
  "topProducts": [
    {
      "name": "Premium Software License",
      "clicks": 450,
      "conversions": 18
    }
  ],
  "geographicData": [
    {
      "country": "US",
      "clicks": 680,
      "conversions": 28
    }
  ]
}
```

**How It Works:**

The backend identifies the user from JWT, retrieves their affiliate profile data, and aggregates click events and conversions with geographic insights.

### Referral Link Generation
POST /affiliate/api/v1/links/generate

**What It Does:**

Creates a unique referral link for a specific product that affiliates can share with their audience.

**Access Control:**

Affiliates only (authentication temporarily disabled for Phase 1 demo).

**Request:**

POST /affiliate/api/v1/links/generate

Authorization: Bearer <JWT>

```json
{
  "productId": "550e8400-e29b-41d4-a716-446655440000"
}
```

**Sample Response:**

```json
{
  "referralCode": "JOHN123-PRE-7f8a"
}
```

**How It Works:**

The backend combines the affiliate's TrackingId with product abbreviation and a unique identifier to create a trackable referral code.

### Public Click Tracking
GET /api/v1/r/{code}

**What It Does:**

Tracks referral link clicks and redirects users to the product page while capturing analytics data.

**Access Control:**

Public endpoint - no authentication required.

**Request:**

GET /api/v1/r/JOHN123-PRE-7f8a?utm_source=twitter

**Sample Response:**

302 Redirect to: https://emutare.com/products/550e8400-e29b-41d4-a716-446655440000?ref=JOHN123-PRE-7f8a

**How It Works:**

The backend captures IP address, user agent, and platform data, enriches it with geo-location information, stores the click event, and redirects to the product page.

### Sale Simulation (Demo)
POST /affiliate/api/v1/dashboard/simulate-sale

**What It Does:**

Simulates a sale conversion for demo purposes to show real-time revenue updates in the dashboard.

**Access Control:**

Affiliates only (temporary Phase 1 demo endpoint).

**Request:**

POST /affiliate/api/v1/dashboard/simulate-sale

Authorization: Bearer <JWT>

```json
{
  "referralCode": "JOHN123-PRE-7f8a",
  "productId": "550e8400-e29b-41d4-a716-446655440000",
  "amount": 299.99,
  "country": "US"
}
```

**Sample Response:**

```json
{
  "message": "Sale Simulated Successfully. Refresh dashboard to see updates."
}
```

**How It Works:**

The backend validates the referral code and product, creates a conversion record with 10% commission, and updates the affiliate's revenue metrics.

### Global Admin Dashboard
GET /api/dashboard/summary

**What It Does:**

Returns system-wide analytics for administrators including top products, countries, and overall revenue.

**Access Control:**

Administrators only (authorization temporarily disabled for Phase 1).

**Request:**

GET /api/dashboard/summary

Authorization: Bearer <JWT>

**Sample Response:**

```json
{
  "totalRevenue": 45750.00,
  "totalClicks": 15420,
  "totalConversions": 183,
  "topProduct": {
    "name": "Premium Software License",
    "revenue": 18250.00
  },
  "topCountry": {
    "name": "United States",
    "revenue": 28900.00
  }
}
```

**How It Works:**

The backend aggregates data across all affiliates, products, and geographic regions to provide comprehensive system insights.

### Commission Rate Management
PUT /affiliate/api/v1/admin/commission-rate

**What It Does:**

Updates the global commission rate for all products and logs the change for audit purposes.

**Access Control:**

Admin and Support roles only (authorization temporarily disabled for Phase 1).

**Request:**

PUT /affiliate/api/v1/admin/commission-rate

Authorization: Bearer <JWT>

```json
25.5
```

**Sample Response:**

```json
{
  "message": "Global commission rate updated successfully"
}
```

**How It Works:**

The backend updates the global commission setting in the database and publishes the change to Kafka for audit logging and system synchronization.

### Audit Log Access
GET /affiliate/api/v1/admin/audit-logs/{entityName}

**What It Does:**

Retrieves audit logs for a specific entity to support fraud investigation and compliance monitoring.

**Access Control:**

Admin and Support roles only (authorization temporarily disabled for Phase 1).

**Request:**

GET /affiliate/api/v1/admin/audit-logs/AffiliateProfile

Authorization: Bearer <JWT>

**Sample Response:**

```json
[
  {
    "entityName": "AffiliateProfile",
    "action": "Register",
    "newValues": "User: 550e8400-e29b-41d4-a716-446655440000, TrackingId: JOHN123",
    "performedBy": "System_User",
    "createdAt": "2026-03-10T19:15:30Z"
  }
]
```

**How It Works:**

The backend queries the audit logs for the specified entity type, returns the 50 most recent entries, and includes detailed change tracking for security investigations.

## Business Logic

### Self-Referral Block (Anti-Fraud System)

The system implements a critical security feature to prevent affiliates from earning commissions on their own purchases:

**Implementation in `ValidateReferralHandler`:**

1. **Detection Logic**
   ```csharp
   if (link.AffiliateProfile.UserId == request.PurchasingUserId)
   {
       // Self-referral detected
   }
   ```

2. **Security Logging**
   - Creates audit log entry with "Security_Alert" entity name
   - Records "Self_Referral_Blocked" action
   - Captures user ID and referral code for investigation

3. **User Response**
   - Returns clear fraud alert message: "You cannot use your own referral link for discounts"
   - Prevents commission calculation for self-referrals

4. **Business Rationale**
   - Protects affiliate program integrity
   - Prevents commission fraud
   - Maintains fair marketplace practices
   - Provides audit trail for compliance

This security measure is referenced in Section 8 of the Business Plan, emphasizing that "Security is the most important aspect" of the affiliate marketing system.

## Common Errors and Troubleshooting

**400 – Bad Request**
This error is returned when the request body is missing required fields or includes invalid input types. Ensure all expected parameters (e.g., usernames, emails, product IDs) are correctly provided and meet validation rules (username min 3 chars, password min 8 chars, valid email format).

**401 – Unauthorised**
Occurs when the JWT token is missing or invalid. Make sure the request includes a valid Authorization: Bearer <token> header with required claims (UserId, UserRole). Note: Authentication is temporarily disabled for Phase 1 demo.

**403 – Forbidden**
This response indicates the user's role lacks permission to access the route. Confirm that the logged-in role (Admin, Support, Affiliate) is authorised to perform the action based on your access policy.

**404 – Not Found**
Triggered when a resource (e.g., product, affiliate profile, referral link) does not exist. Double-check all IDs and parameters passed in the URL or request body.

**409 – Conflict**
Returned when trying to create a record that already exists, such as an affiliate with the same UserId or TrackingId. Use unique values to avoid duplication and don't attempt self-referrals (intentional fraud prevention).

**500 – Internal Server Error**
Represents a failure in backend logic or a server crash. Check logs for stack traces related to database connections, Kafka/Redis services, or external API timeouts. Verify environment variables (KAFKA_BOOTSTRAP_SERVERS, REDIS_CONNECTION) are properly configured.

## Technology Stack

- **.NET 8** - Core framework
- **ASP.NET Core Web API** - RESTful services
- **PostgreSQL** - Primary database
- **Apache Kafka** - Event streaming and audit logging
- **MediatR** - CQRS pattern implementation
- **Entity Framework Core** - ORM
- **IpInfo** - Geo-location services
- **Docker** - Containerization

## Key Features

- **Real-time click tracking** with geo-location enrichment
- **Fraud prevention** through self-referral blocking
- **Comprehensive analytics** for affiliates and administrators
- **Event-driven architecture** with Kafka integration
- **Secure audit logging** for compliance
- **Scalable microservices** design
