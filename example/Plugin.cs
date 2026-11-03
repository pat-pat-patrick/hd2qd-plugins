using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Windows;
using System.Windows.Controls;

namespace Hd2Qd.Example
{
    /// <summary>The smallest plugin that uses every call HD2 Mod Quick Deploy makes. The manager
    /// finds the one public class named Plugin in an HD2QD.*.dll and calls it by name; nothing
    /// is shared with it but strings, numbers, bools, delegates and Json shapes (Dictionary of
    /// string to object, List of object, long, double, string, bool).</summary>
    public static class Plugin
    {
        /// <summary>The contract's version. A plugin of another one is refused.</summary>
        public const int Api = 2;

        /// <summary>"window": a window of its own, opened from the card (Open). "panel": the
        /// plugin draws the card's body on the Plugins page (Panel).</summary>
        public const string Kind = "window";

        /// <summary>In lang, a language tag ("en", "zh-CN"): the text comes from that language's
        /// file, else English (Words).</summary>
        public static string Title(string lang) => Words.Get(lang, "title");

        public static string Summary(string lang) => Words.Get(lang, "summary");

        /// <summary>Kind "window": the card's Open. host["window"](title, content) makes a window
        /// with the manager's own frame; host["mods"]() gives the enabled mods in load order.</summary>
        public static void Open(Window owner, Dictionary<string, object> host)
        {
            var lang = Words.Lang(host);
            var mods = ((Func<List<Dictionary<string, object>>>)host["mods"])();
            var list = new StackPanel { Margin = new Thickness(24) };
            foreach (var m in mods)
                list.Children.Add(new TextBlock
                {
                    Text = m["name"] + "  ·  " + Words.F(lang, "archives", ((List<object>)m["archives"]).Count),
                    Margin = new Thickness(0, 4, 0, 4),
                });
            var make = (Func<string, FrameworkElement, Window>)host["window"];
            make(Title(lang), new ScrollViewer { Content = list }).Show();
        }

        /// <summary>Optional: a word on a mod's row, or null, in host["lang"]; colour is "Yellow",
        /// "Blue" or "Muted". Called for every mod whenever the manager reads its state: keep it
        /// cheap.</summary>
        public static Dictionary<string, object> ModNote(string modFolder, Dictionary<string, object> host) =>
            File.Exists(Path.Combine(modFolder, "example_note.txt"))
                ? new Dictionary<string, object>
                {
                    ["text"] = Words.Get(Words.Lang(host), "note"), ["tip"] = Words.Get(Words.Lang(host), "note_tip"),
                    ["colour"] = "Blue",
                }
                : null;

        /// <summary>Optional: commands added to the manager's command line, as rows of [name,
        /// help]. A name the manager has itself is left out.</summary>
        public static readonly string[][] Commands =
        {
            new[] { "example-count", "how many mods are enabled" },
        };

        /// <summary>Optional, with Commands: 0 done, 1 refused, 2 a wrong command line. What it
        /// throws is reported as a refusal.</summary>
        public static int Run(string command, string[] args, TextWriter output, Dictionary<string, object> host)
        {
            var mods = ((Func<List<Dictionary<string, object>>>)host["mods"])();
            output.WriteLine(mods.Count + " mods enabled");
            return 0;
        }

        /// <summary>Optional: runs once in the background when the manager's window starts (a
        /// renewal, a cache). True when it changed something the manager should read again.</summary>
        public static bool Start(Dictionary<string, object> host) => false;
    }
}
