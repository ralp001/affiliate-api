using Affiliate.Events;

namespace Affiliate.Application.Abstractions;

public interface ISchemaDiscoveryService
{
    /// <summary>
    /// Scans the provided entity types and generates a list of table definitions 
    /// along with a unique SHA256 hash of the schema structure.
    /// </summary>
    /// <param name="entities">List of domain entity types to inspect.</param>
    /// <returns>A tuple containing the list of TableSchemas and the unique Hash string.</returns>
    (List<TableSchema> Tables, string Hash) DiscoverSchema(List<Type> entities);
}