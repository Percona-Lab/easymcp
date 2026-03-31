#!/usr/bin/env node
/**
 * easymcp npm wrapper
 *
 * Thin bridge so Node.js users can run: npx easymcp init
 *
 * This installs uv (if needed) and delegates to the Python CLI:
 *   uvx easymcp <args>
 */

import { execSync, spawnSync } from "child_process";
import { platform } from "os";

function hasCommand(cmd) {
  try {
    execSync(`${platform() === "win32" ? "where" : "which"} ${cmd}`, {
      stdio: "ignore",
    });
    return true;
  } catch {
    return false;
  }
}

function installUv() {
  console.log("  Installing uv (Python package manager)...");
  try {
    if (platform() === "win32") {
      execSync(
        'powershell -ExecutionPolicy Bypass -c "irm https://astral.sh/uv/install.ps1 | iex"',
        { stdio: "inherit" }
      );
    } else {
      execSync("curl -LsSf https://astral.sh/uv/install.sh | sh", {
        stdio: "inherit",
      });
    }
    // Add common install paths
    const sep = platform() === "win32" ? ";" : ":";
    const home = process.env.HOME || process.env.USERPROFILE || "";
    process.env.PATH = `${home}/.local/bin${sep}${home}/.cargo/bin${sep}${process.env.PATH}`;

    if (!hasCommand("uv")) {
      console.error(
        "  uv installed but not in PATH. Please restart your shell and re-run."
      );
      process.exit(1);
    }
    console.log("  uv installed.");
  } catch (err) {
    console.error(`  Failed to install uv: ${err.message}`);
    console.error(
      "  Install manually: https://docs.astral.sh/uv/getting-started/installation/"
    );
    process.exit(1);
  }
}

// Ensure uv is available
if (!hasCommand("uv")) {
  installUv();
}

// Forward all arguments to uvx easymcp
const args = process.argv.slice(2);
const result = spawnSync("uvx", ["easymcp", ...args], {
  stdio: "inherit",
  env: process.env,
});

process.exit(result.status ?? 1);
