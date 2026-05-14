using System;
using Microsoft.EntityFrameworkCore.Migrations;

#nullable disable

namespace AffiliateMarketing.Infrastructure.Migrations
{
    /// <inheritdoc />
    public partial class SyncDemoData : Migration
    {
        /// <inheritdoc />
        protected override void Up(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.DeleteData(
                table: "Products",
                keyColumn: "Id",
                keyValue: new Guid("44444444-4444-4444-4444-444444444444"));

            migrationBuilder.InsertData(
                table: "AffiliateProfiles",
                columns: new[] { "Id", "CreatedAt", "IsActive", "TrackingId", "UserId" },
                values: new object[] { new Guid("bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb"), new DateTime(2026, 1, 1, 0, 0, 0, 0, DateTimeKind.Utc), true, "JIMMY_DEMO_PROFILE", new Guid("11111111-1111-1111-1111-111111111111") });

            migrationBuilder.InsertData(
                table: "ReferralLinks",
                columns: new[] { "Id", "AffiliateProfileId", "CreatedAt", "GeneratedCode", "IsActive", "ProductId", "SourcePlatform" },
                values: new object[] { new Guid("77777777-7777-7777-7777-777777777777"), new Guid("bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb"), new DateTime(2026, 1, 1, 0, 0, 0, 0, DateTimeKind.Utc), "JIMMY_DEMO", true, new Guid("33333333-3333-3333-3333-333333333333"), null });
        }

        /// <inheritdoc />
        protected override void Down(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.DeleteData(
                table: "ReferralLinks",
                keyColumn: "Id",
                keyValue: new Guid("77777777-7777-7777-7777-777777777777"));

            migrationBuilder.DeleteData(
                table: "AffiliateProfiles",
                keyColumn: "Id",
                keyValue: new Guid("bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb"));

            migrationBuilder.InsertData(
                table: "Products",
                columns: new[] { "Id", "BasePrice", "CommissionType", "CommissionValue", "Currency", "Description", "IsAvailableForAffiliates", "Name", "ProductType", "SubscriptionPlan" },
                values: new object[] { new Guid("44444444-4444-4444-4444-444444444444"), 25000m, 1, 15m, "NGN", "Enterprise level affiliate management", true, "Nixus", "Business", "Platinum" });
        }
    }
}
