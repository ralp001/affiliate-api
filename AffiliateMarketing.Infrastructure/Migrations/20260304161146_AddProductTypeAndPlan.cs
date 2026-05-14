using System;
using Microsoft.EntityFrameworkCore.Migrations;

#nullable disable

#pragma warning disable CA1814 // Prefer jagged arrays over multidimensional

namespace AffiliateMarketing.Infrastructure.Migrations
{
    /// <inheritdoc />
    public partial class AddProductTypeAndPlan : Migration
    {
        /// <inheritdoc />
        protected override void Up(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.DeleteData(
                table: "ClickEvents",
                keyColumn: "Id",
                keyValue: new Guid("44444444-4444-4444-4444-444444444444"));

            migrationBuilder.DeleteData(
                table: "Products",
                keyColumn: "Id",
                keyValue: new Guid("22222222-2222-2222-2222-222222222222"));

            migrationBuilder.AddColumn<string>(
                name: "ProductType",
                table: "Products",
                type: "text",
                nullable: false,
                defaultValue: "");

            migrationBuilder.AddColumn<string>(
                name: "SubscriptionPlan",
                table: "Products",
                type: "text",
                nullable: false,
                defaultValue: "");

            migrationBuilder.InsertData(
                table: "ClickEvents",
                columns: new[] { "Id", "City", "ClickedAt", "CountryCode", "IpAddress", "Location", "Platform", "ProductId", "Region", "TrackingId", "UserAgent" },
                values: new object[] { new Guid("55555555-5555-5555-5555-555555555555"), "Onitsha", new DateTime(2026, 1, 1, 0, 0, 0, 0, DateTimeKind.Utc), "NG", "102.89.1.1", "Onitsha, NG", null, new Guid("33333333-3333-3333-3333-333333333333"), null, "JIMMY_DEMO", null });

            migrationBuilder.InsertData(
                table: "Products",
                columns: new[] { "Id", "BasePrice", "CommissionType", "CommissionValue", "Currency", "Description", "IsAvailableForAffiliates", "Name", "ProductType", "SubscriptionPlan" },
                values: new object[,]
                {
                    { new Guid("33333333-3333-3333-3333-333333333333"), 5000m, 1, 10m, "NGN", "Affiliate tracking for individuals", true, "Emutare Idex", "Individual", "Gold" },
                    { new Guid("44444444-4444-4444-4444-444444444444"), 25000m, 1, 15m, "NGN", "Enterprise level affiliate management", true, "Nixus", "Business", "Platinum" }
                });
        }

        /// <inheritdoc />
        protected override void Down(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.DeleteData(
                table: "ClickEvents",
                keyColumn: "Id",
                keyValue: new Guid("55555555-5555-5555-5555-555555555555"));

            migrationBuilder.DeleteData(
                table: "Products",
                keyColumn: "Id",
                keyValue: new Guid("33333333-3333-3333-3333-333333333333"));

            migrationBuilder.DeleteData(
                table: "Products",
                keyColumn: "Id",
                keyValue: new Guid("44444444-4444-4444-4444-444444444444"));

            migrationBuilder.DropColumn(
                name: "ProductType",
                table: "Products");

            migrationBuilder.DropColumn(
                name: "SubscriptionPlan",
                table: "Products");

            migrationBuilder.InsertData(
                table: "ClickEvents",
                columns: new[] { "Id", "City", "ClickedAt", "CountryCode", "IpAddress", "Location", "Platform", "ProductId", "Region", "TrackingId", "UserAgent" },
                values: new object[] { new Guid("44444444-4444-4444-4444-444444444444"), "Lagos", new DateTime(2026, 1, 1, 0, 0, 0, 0, DateTimeKind.Utc), "NG", "127.0.0.1", "Lagos, NG", null, new Guid("22222222-2222-2222-2222-222222222222"), null, "JIMMY123", "Mozilla/5.0 (Windows NT 10.0; Win64; x64)" });

            migrationBuilder.InsertData(
                table: "Products",
                columns: new[] { "Id", "BasePrice", "CommissionType", "CommissionValue", "Currency", "Description", "IsAvailableForAffiliates", "Name" },
                values: new object[] { new Guid("22222222-2222-2222-2222-222222222222"), 75000m, 1, 15m, "NGN", "Enterprise-grade cybersecurity training and role-play simulation.", true, "CyberRole Defense Pro" });
        }
    }
}
