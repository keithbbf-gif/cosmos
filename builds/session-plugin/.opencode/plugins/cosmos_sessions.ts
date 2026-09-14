// OpenWork / opencode plugin entry. Adapter only — every behaviour lives in
// ../../src/tools.ts so the MCP host and this host get exactly the same product.
//
// Registered from the sibling opencode.json. Nothing is imported from the vendor
// SDK: the plugin input is structurally typed below, so a vendor API change
// breaks this one file instead of the tool table.

import { runTool, SESSION_TOOLS } from "../../src/tools.ts";
import type { ToolContext } from "../../src/tools.ts";

type PluginInput = {
  directory?: string;
  worktree?: string;
};

type HostTool = {
  description: string;
  args: unknown;
  parameters: unknown;
  execute: (args: Record<string, unknown>) => Promise<string>;
};

type PluginHooks = { tool: Record<string, HostTool> };

function hostTool(def: (typeof SESSION_TOOLS)[number]): HostTool {
  return {
    description: def.description,
    // Both spellings: opencode reads `args`, several forks read `parameters`.
    args: def.inputSchema,
    parameters: def.inputSchema,
    execute: async (args: Record<string, unknown> = {}) => {
      // Config is read from the host process environment at call time. The
      // plugin holds no credential and caches none.
      const ctx: ToolContext = { env: process.env };
      return JSON.stringify(await runTool(def.name, args, ctx), null, 2);
    },
  };
}

export const CosmosSessionsPlugin = async (_input: PluginInput = {}): Promise<PluginHooks> => {
  const tool: Record<string, HostTool> = {};
  for (const def of SESSION_TOOLS) {
    const entry = hostTool(def);
    tool[def.id] = entry;
    if (def.name !== def.id) {
      tool[def.name] = entry;
    }
  }
  return { tool };
};

export default CosmosSessionsPlugin;
