using System;
using System.Collections.Generic;
using System.Text;

namespace AffiliateMarketing.Application.Common.Security
{
    public interface IRequirePermission
    {
        string FieldPath { get; }
        string Action { get; }
    }
}
