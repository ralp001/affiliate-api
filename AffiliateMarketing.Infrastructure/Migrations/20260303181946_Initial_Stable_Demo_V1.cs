using System;
using Microsoft.EntityFrameworkCore.Migrations;

#nullable disable

namespace AffiliateMarketing.Infrastructure.Migrations
{
    /// <inheritdoc />
    public partial class Initial_Stable_Demo_V1 : Migration
    {
        /// <inheritdoc />
        protected override void Up(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.DropIndex(
                name: "IX_ReferralLinks_GeneratedCode",
                table: "ReferralLinks");

            migrationBuilder.InsertData(
                table: "ClickEvents",
                columns: new[] { "Id", "City", "ClickedAt", "CountryCode", "IpAddress", "Location", "Platform", "ProductId", "Region", "TrackingId", "UserAgent" },
                values: new object[] { new Guid("44444444-4444-4444-4444-444444444444"), "Lagos", new DateTime(2026, 1, 1, 0, 0, 0, 0, DateTimeKind.Utc), "NG", "127.0.0.1", "Lagos, NG", null, new Guid("22222222-2222-2222-2222-222222222222"), null, "JIMMY123", "Mozilla/5.0 (Windows NT 10.0; Win64; x64)" });

            migrationBuilder.InsertData(
                table: "Products",
                columns: new[] { "Id", "BasePrice", "CommissionType", "CommissionValue", "Currency", "Description", "IsAvailableForAffiliates", "Name" },
                values: new object[] { new Guid("22222222-2222-2222-2222-222222222222"), 75000m, 1, 15m, "NGN", "Enterprise-grade cybersecurity training and role-play simulation.", true, "CyberRole Defense Pro" });

            migrationBuilder.UpdateData(
                table: "Users",
                keyColumn: "Id",
                keyValue: new Guid("11111111-1111-1111-1111-111111111111"),
                columns: new[] { "CreatedAt", "HomeCountry", "PasswordHash", "Username" },
                values: new object[] { new DateTime(2026, 1, 1, 0, 0, 0, 0, DateTimeKind.Utc), "Nigeria", "secure_hash", "Jimmy_Affiliate" });

            migrationBuilder.CreateIndex(
                name: "IX_Conversions_CustomerCountry",
                table: "Conversions",
                column: "CustomerCountry");

            migrationBuilder.CreateIndex(
                name: "IX_ClickEvents_CountryCode",
                table: "ClickEvents",
                column: "CountryCode");
        }

        /// <inheritdoc />
        protected override void Down(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.DropIndex(
                name: "IX_Conversions_CustomerCountry",
                table: "Conversions");

            migrationBuilder.DropIndex(
                name: "IX_ClickEvents_CountryCode",
                table: "ClickEvents");

            migrationBuilder.DeleteData(
                table: "ClickEvents",
                keyColumn: "Id",
                keyValue: new Guid("44444444-4444-4444-4444-444444444444"));

            migrationBuilder.DeleteData(
                table: "Products",
                keyColumn: "Id",
                keyValue: new Guid("22222222-2222-2222-2222-222222222222"));

            migrationBuilder.UpdateData(
                table: "Users",
                keyColumn: "Id",
                keyValue: new Guid("11111111-1111-1111-1111-111111111111"),
                columns: new[] { "CreatedAt", "HomeCountry", "PasswordHash", "Username" },
                values: new object[] { new DateTime(2024, 1, 1, 12, 0, 0, 0, DateTimeKind.Utc), "Unknown", "hashed_pw", "demo_affiliate" });

            migrationBuilder.CreateIndex(
                name: "IX_ReferralLinks_GeneratedCode",
                table: "ReferralLinks",
                column: "GeneratedCode",
                unique: true);
        }
    }
}
