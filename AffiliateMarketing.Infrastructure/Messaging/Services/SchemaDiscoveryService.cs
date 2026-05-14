using System.Reflection;
using System.Security.Cryptography;
using System.Text;
using System.Text.Json; // Use System.Text.Json for consistent hashing
using Affiliate.Application.Abstractions;
using Affiliate.Events;

namespace AffiliateMarketing.Infrastructure.Services;

public class SchemaDiscoveryService : ISchemaDiscoveryService
{
    public (List<TableSchema> Tables, string Hash) DiscoverSchema(List<Type> entities)
    {
        var schemas = new List<TableSchema>();

        foreach (var entity in entities)
        {
            var table = new TableSchema
            {
                // Consistent with Product/Ticketing: pluralize table names
                table_name = entity.Name.ToLower() + "s",

                // CRITICAL: Property name must be 'data_types' to match the UI
                data_types = entity.GetProperties(BindingFlags.Public | BindingFlags.Instance)
                    .Select(p => new DataTypeInfo
                    {
                        // CRITICAL: Keys must be 'field_name' and 'field_type'
                        field_name = p.Name.ToLower(),
                        field_type = GetSimplifiedType(p.PropertyType)
                    }).ToList()
            };

            schemas.Add(table);
        }

        // Generate hash using JSON serialization (matches Product API logic)
        var hash = GenerateHash(schemas);
        return (schemas, hash);
    }

    private string GetSimplifiedType(Type type)
    {
        var nullableType = Nullable.GetUnderlyingType(type);
        var actualType = nullableType ?? type;

        if (actualType == typeof(Guid)) return "uuid";
        if (actualType == typeof(string)) return "string";
        if (actualType == typeof(int) || actualType == typeof(long)) return "integer";
        if (actualType == typeof(decimal) || actualType == typeof(double)) return "float"; // Chibuikem expects 'float' or 'decimal'
        if (actualType == typeof(bool)) return "boolean";
        if (actualType == typeof(DateTime)) return "datetime"; // Use 'datetime' to match others
        if (actualType.IsEnum) return "enum";

        return "string"; // Default to string for safety
    }

    private string GenerateHash(List<TableSchema> schemas)
    {
        var json = JsonSerializer.Serialize(schemas);
        var bytes = SHA256.HashData(Encoding.UTF8.GetBytes(json));
        return BitConverter.ToString(bytes).Replace("-", "").ToLower();
    }
}