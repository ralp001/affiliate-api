using System;

class Program
{
    static void Main()
    {
        var password = "Password123!";
        var hash = BCrypt.Net.BCrypt.HashPassword(password);

        Console.WriteLine("Generated BCrypt Hash:");
        Console.WriteLine(hash);

        Console.ReadLine();
    }
}
