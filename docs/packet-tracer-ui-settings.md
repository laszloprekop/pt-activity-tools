# Packet Tracer: stop windows jumping around and fonts changing size

Practical settings for Packet Tracer 8.x and 9.x on macOS and Windows. "Documented" means it is in Cisco's help pages; "observed" means it was checked on the Mac used for this project (Packet Tracer 8.0.0, 8.2.2 and 9.0.1 on macOS 26); "tip" means a general macOS, Windows or Qt behaviour that applies to Packet Tracer but was not measured here.

## Why it happens

Packet Tracer is a Qt application. Three things make it feel unstable:

- Every device you open gets its own floating window, placed at a default position, and those windows are hidden whenever Packet Tracer is not the active application (observed). Nothing remembers where you dragged them.
- The instructions window of an activity ("PT Activity") is a separate floating window too.
- Text size comes from four different places: the application font size, the CLI font, the tooltip font, and, inside an activity, the HTML of the instructions, which carries its own font sizes from whoever wrote the activity (the 2007 files set theirs explicitly). On a Mac with a Retina display and an external monitor, Qt also rescales a window when it moves between screens with different scaling.

## Keep the windows where you put them

1. **Dock the instructions.** At the bottom of the PT Activity window there are two check boxes: "Keep Instructions on top" and "Dock instructions to the left" (observed in 8.0.0 and 9.0.1). Tick "Dock instructions to the left" and the instructions become a panel inside the main window instead of a floating window. Tick "Keep Instructions on top" if you prefer it floating but never hidden behind the workspace.
2. **Turn on the device dialog taskbar.** Options, Preferences, Interface tab, "Show Device Dialog Taskbar" (documented; the same switch also appears on the Miscellaneous tab). Open device windows are then listed in a bar inside the main window, so you can bring one back with one click instead of hunting for it behind other applications.
3. **Use one maximised window, not macOS full screen** (tip). The green button puts Packet Tracer in its own Space; its floating dialogs then open on other Spaces or disappear when you switch. Double-click the title bar, or hold Option and click the green button, to maximise instead.
4. **Keep Packet Tracer on one display** (tip). Moving the main window to a screen with a different scale factor re-lays-out everything and resizes the dialogs. On a laptop with an external monitor, decide which screen Packet Tracer lives on and leave it there.
5. **Reset a window that comes up off-screen or tiny.** Packet Tracer stores its window state in its user folder: `~/Cisco Packet Tracer <version>/PT.conf` on macOS, `%USERPROFILE%\Cisco Packet Tracer <version>\PT.conf` on Windows (observed on macOS). Quit Packet Tracer, rename `PT.conf` to `PT.conf.bak`, start again: the window geometry and all preferences return to defaults. Use this only when a window is unreachable, because it also resets the font settings below. On Windows, Shift + right-click on the taskbar button, "Move", then arrow keys also brings an off-screen window back (tip).

## Make the fonts consistent

Open Options, Preferences, Font tab (documented):

- **Application Global Size** slider: scales the fonts and icons of the whole interface and all dialogs. Set it once, click Apply. This is the one that fixes "everything is tiny on my 4K screen" or "everything is huge on my laptop".
- **CLI** font and size: the terminal inside routers and switches. Pick a monospaced font (Menlo on macOS, Consolas on Windows) and a size that matches the rest.
- **Tooltips** font and size.
- Older 8.x builds list the same settings as Dialogs, Workspace/Activity Wizard and General Interface fonts; set all three to the same family and size.
- **Font colours** for Router IOS text and background and PC console text and background are on the same tab, useful if the default colours look washed out on your display.

Then, if you want the settings to survive a reset or apply to every user on a shared machine: Options, Preferences, Administrative tab, "Write" saves the current `PT.conf` globally (documented).

Two things the Font tab cannot change:

- The text inside an activity's instructions window is HTML written into the activity file. Its size comes from the file, not from Packet Tracer. The converted files in this repository keep the original HTML on purpose.
- The size difference between a Retina and a non-Retina screen on macOS. See the next section.

## High-DPI scaling, by platform

**Windows** (documented by Cisco, repeated on the Cisco Community): if the interface is blurry or the wrong size on a high-resolution screen, right-click the Packet Tracer shortcut, Properties, Compatibility, "Change high DPI settings", tick "Override high DPI scaling behaviour", and choose "Scaling performed by: System (Enhanced)". Then use the Application Global Size slider for the final size.

**macOS**: Qt handles Retina scaling itself. If the mix of a Retina laptop screen and a non-Retina monitor gives you two different sizes, either keep Packet Tracer on one screen, or set both screens to the same effective scaling in System Settings, Displays. As a last resort you can start Packet Tracer from Terminal with a fixed Qt scale factor; this was tested once with 9.0.1 and the interface came up about one and a half times larger (observed):

```bash
env QT_SCALE_FACTOR=1.5 "/Applications/Cisco Packet Tracer 9.0.1/Cisco Packet Tracer 9.0.1.app/Contents/MacOS/PacketTracer"
```

Other Qt variables that work the same way (tip): `QT_AUTO_SCREEN_SCALE_FACTOR=0` to stop per-screen rescaling, `QT_SCREEN_SCALE_FACTORS="2;1"` to give each screen its own factor, `QT_FONT_DPI=96` to change only the text. On Windows these can be set as user environment variables (System Properties, Environment Variables) and then apply to every start. Setting a factor of 2 doubles fonts but quadruples widget area, so prefer values between 1 and 1.5.

## A checklist for a new installation

1. Options, Preferences, Font: set Application Global Size, CLI font and Tooltips font. Apply.
2. Options, Preferences, Interface: tick "Show Device Dialog Taskbar".
3. Open any activity, tick "Dock instructions to the left" in the PT Activity window.
4. Maximise the main window (not full screen on macOS) and leave it on one display.
5. Optional: Options, Preferences, Administrative, "Write", so the settings are kept.

## Sources

- Cisco, Packet Tracer help: Settings and Preferences, https://tutorials.ptnetacad.net/help/default/preferences.htm
- Cisco, Packet Tracer help: Font preferences, https://tutorials.ptnetacad.net/help/default/fontPreference.htm
- Cisco, Packet Tracer help: High DPI scaling, https://tutorials.ptnetacad.net/help/default/large_Interface.htm
- Cisco Community, "Packet Tracer UI is too large to work" (Windows high DPI override steps), https://community.cisco.com/t5/switching/packet-tracer-ui-is-too-large-to-work/m-p/4471781
- Cisco Community, "How to change the text size in CLI", https://community.cisco.com/t5/discusiones-routing-y-switching/how-to-change-the-text-size-in-cli/m-p/4797165
