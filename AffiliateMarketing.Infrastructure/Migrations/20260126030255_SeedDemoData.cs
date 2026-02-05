using System;
using Microsoft.EntityFrameworkCore.Migrations;

#nullable disable

#pragma warning disable CA1814 // Prefer jagged arrays over multidimensional

namespace AffiliateMarketing.Infrastructure.Migrations
{
    /// <inheritdoc />
    public partial class SeedDemoData : Migration
    {
        /// <inheritdoc />
        protected override void Up(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.InsertData(
                table: "AffiliateProfiles",
                columns: new[] { "Id", "CreatedAt", "TrackingId", "UserId" },
                values: new object[] { new Guid("33333333-3333-3333-3333-333333333333"), new DateTime(2024, 1, 1, 12, 0, 0, 0, DateTimeKind.Utc), "DEMO123", new Guid("11111111-1111-1111-1111-111111111111") });

            migrationBuilder.InsertData(
                table: "ClickEvents",
                columns: new[] { "Id", "ClickedAt", "IpAddress", "TrackingId", "UserAgent" },
                values: new object[,]
                {
                    { new Guid("44444444-4444-4444-4444-444444444444"), new DateTime(2024, 1, 1, 11, 50, 0, 0, DateTimeKind.Utc), "127.0.0.1", "DEMO123", "Mozilla/5.0" },
                    { new Guid("55555555-5555-5555-5555-555555555555"), new DateTime(2024, 1, 1, 11, 55, 0, 0, DateTimeKind.Utc), "127.0.0.1", "DEMO123", "Chrome" }
                });

            migrationBuilder.InsertData(
                table: "Products",
                columns: new[] { "Id", "CommissionType", "CommissionValue", "Name" },
                values: new object[] { new Guid("22222222-2222-2222-2222-222222222222"), "percentage", 60m, "Startup Plan" });

            migrationBuilder.InsertData(
                table: "Users",
                columns: new[] { "Id", "CreatedAt", "PasswordHash", "Role", "Username" },
                values: new object[] { new Guid("11111111-1111-1111-1111-111111111111"), new DateTime(2024, 1, 1, 12, 0, 0, 0, DateTimeKind.Utc), "$2a$11$BMPxjYU01aj1TVGEyqnHaejKA9aZyXnDCKl5ER4jb7h28goYYGczC", "Affiliate", "demo_affiliate" });
        }

        /// <inheritdoc />
        protected override void Down(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.DeleteData(
                table: "AffiliateProfiles",
                keyColumn: "Id",
                keyValue: new Guid("33333333-3333-3333-3333-333333333333"));

            migrationBuilder.DeleteData(
                table: "ClickEvents",
                keyColumn: "Id",
                keyValue: new Guid("44444444-4444-4444-4444-444444444444"));

            migrationBuilder.DeleteData(
                table: "ClickEvents",
                keyColumn: "Id",
                keyValue: new Guid("55555555-5555-5555-5555-555555555555"));

            migrationBuilder.DeleteData(
                table: "Products",
                keyColumn: "Id",
                keyValue: new Guid("22222222-2222-2222-2222-222222222222"));

            migrationBuilder.DeleteData(
                table: "Users",
                keyColumn: "Id",
                keyValue: new Guid("11111111-1111-1111-1111-111111111111"));
        }
    }
}
