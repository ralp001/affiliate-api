using System;
using System.Collections.Generic;
using System.Text;

namespace AffiliateMarketing.Infrastructure.Security.Jwt
{
    public class JwtOptions
    {
        public string InternalSecret { get; set; } = null!;
        public string ExternalSecret { get; set; } = null!;
        public string Algorithm { get; set; } = "HS256";
    }
}
