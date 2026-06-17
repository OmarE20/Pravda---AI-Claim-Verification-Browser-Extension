import * as esbuild from "esbuild";

const watch = process.argv.includes("--watch");

const options = {
  entryPoints: {
    "content-script": "content-script.ts",
    background: "background.ts",
    sidepanel: "sidepanel/panel.ts",
  },
  bundle: true,
  outdir: "dist",
  format: "iife",
  target: "chrome110",
  sourcemap: true,
};

if (watch) {
  const ctx = await esbuild.context(options);
  await ctx.watch();
  console.log("Watching for changes...");
} else {
  await esbuild.build(options);
  console.log("Build complete -> dist/");
}
