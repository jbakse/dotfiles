import AppKit
let args = CommandLine.arguments
let out = args[1]
for p in args.dropFirst(2) {
  let img = NSWorkspace.shared.icon(forFile: p)
  let size = NSSize(width: 96, height: 96)
  let rep = NSBitmapImageRep(bitmapDataPlanes: nil, pixelsWide: 96, pixelsHigh: 96, bitsPerSample: 8, samplesPerPixel: 4, hasAlpha: true, isPlanar: false, colorSpaceName: .deviceRGB, bytesPerRow: 0, bitsPerPixel: 0)!
  NSGraphicsContext.saveGraphicsState()
  NSGraphicsContext.current = NSGraphicsContext(bitmapImageRep: rep)
  img.draw(in: NSRect(origin: .zero, size: size))
  NSGraphicsContext.restoreGraphicsState()
  let name = (p as NSString).lastPathComponent
  try! rep.representation(using: .png, properties: [:])!.write(to: URL(fileURLWithPath: out + "/" + name + ".png"))
}
