using System;
using Microsoft.EntityFrameworkCore.Migrations;

#nullable disable

namespace AffiliateMarketing.Infrastructure.Migrations
{
    /// <inheritdoc />
    public partial class FinalDemoSeeds : Migration
    {
        /// <inheritdoc />
        protected override void Up(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.UpdateData(
                table: "AffiliateProfiles",
                keyColumn: "Id",
                keyValue: new Guid("bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb"),
                column: "TrackingId",
                value: "JIMMY_PROFILE");

            migrationBuilder.InsertData(
                table: "AffiliateProfiles",
                columns: new[] { "Id", "CreatedAt", "IsActive", "TrackingId", "UserId" },
                values: new object[] { new Guid("cccccccc-cccc-cccc-cccc-cccccccccccc"), new DateTime(2026, 1, 6, 0, 0, 0, 0, DateTimeKind.Utc), true, "AUSSIE_PROFILE", new Guid("aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa") });

            migrationBuilder.InsertData(
                table: "ClickEvents",
                columns: new[] { "Id", "City", "ClickedAt", "CountryCode", "IpAddress", "Location", "Platform", "ProductId", "Region", "TrackingId", "UserAgent" },
                values: new object[] { new Guid("99999999-9999-9999-9999-999999999999"), "Sydney", new DateTime(2026, 1, 7, 0, 0, 0, 0, DateTimeKind.Utc), "AU", "1.1.1.1", "Sydney, AU", null, new Guid("44444444-4444-4444-4444-444444444444"), null, "AUSSIE_CODE", null });

            migrationBuilder.UpdateData(
                table: "Products",
                keyColumn: "Id",
                keyValue: new Guid("33333333-3333-3333-3333-333333333333"),
                column: "Description",
                value: "Individual tracking");

            migrationBuilder.InsertData(
                table: "Products",
                columns: new[] { "Id", "BasePrice", "CommissionType", "CommissionValue", "Currency", "Description", "IsAvailableForAffiliates", "Name", "ProductType", "SubscriptionPlan" },
                values: new object[] { new Guid("44444444-4444-4444-4444-444444444444"), 25000m, 1, 15m, "NGN", "Enterprise management", true, "Nixus", "Business", "Platinum" });

            migrationBuilder.UpdateData(
                table: "Users",
                keyColumn: "Id",
                keyValue: new Guid("11111111-1111-1111-1111-111111111111"),
                column: "PasswordHash",
                value: "hash");

            migrationBuilder.InsertData(
                table: "Users",
                columns: new[] { "Id", "CreatedAt", "HomeCountry", "IsVerified", "PasswordHash", "Role", "Username" },
                values: new object[] { new Guid("aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"), new DateTime(2026, 1, 6, 0, 0, 0, 0, DateTimeKind.Utc), "Australia", false, "hash", "Affiliate", "Aussie_Partner" });

            migrationBuilder.InsertData(
                table: "ReferralLinks",
                columns: new[] { "Id", "AffiliateProfileId", "CreatedAt", "GeneratedCode", "IsActive", "ProductId", "SourcePlatform" },
                values: new object[] { new Guid("88888888-8888-8888-8888-888888888888"), new Guid("cccccccc-cccc-cccc-cccc-cccccccccccc"), new DateTime(2026, 1, 6, 0, 0, 0, 0, DateTimeKind.Utc), "AUSSIE_CODE", true, new Guid("44444444-4444-4444-4444-444444444444"), null });
        }

        /// <inheritdoc />
        protected override void Down(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.DeleteData(
                table: "ClickEvents",
                keyColumn: "Id",
                keyValue: new Guid("99999999-9999-9999-9999-999999999999"));

            migrationBuilder.DeleteData(
                table: "ReferralLinks",
                keyColumn: "Id",
                keyValue: new Guid("88888888-8888-8888-8888-888888888888"));

            migrationBuilder.DeleteData(
                table: "Users",
                keyColumn: "Id",
                keyValue: new Guid("aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"));

            migrationBuilder.DeleteData(
                table: "AffiliateProfiles",
                keyColumn: "Id",
                keyValue: new Guid("cccccccc-cccc-cccc-cccc-cccccccccccc"));

            migrationBuilder.DeleteData(
                table: "Products",
                keyColumn: "Id",
                keyValue: new Guid("44444444-4444-4444-4444-444444444444"));

            migrationBuilder.UpdateData(
                table: "AffiliateProfiles",
                keyColumn: "Id",
                keyValue: new Guid("bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb"),
                column: "TrackingId",
                value: "JIMMY_DEMO_PROFILE");

            migrationBuilder.UpdateData(
                table: "Products",
                keyColumn: "Id",
                keyValue: new Guid("33333333-3333-3333-3333-333333333333"),
                column: "Description",
                value: "Affiliate tracking for individuals");

            migrationBuilder.UpdateData(
                table: "Users",
                keyColumn: "Id",
                keyValue: new Guid("11111111-1111-1111-1111-111111111111"),
                column: "PasswordHash",
                value: "secure_hash");
        }
    }
}
