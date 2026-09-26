import { runTool, XTALK_TOOLS } from "../../src/tools.ts";
import type { ToolContext } from "../../src/tools.ts";

type PluginInput = { directory?: string; worktree?: string };
type HostTool = {
  description: string;
  args: unknown;
  parameters: unknown;
  execute: (args: Record<string, unknown>) => Promise<string>;
};
type PluginHooks = { tool: Record<string, HostTool> };

export const CosmosXTalkPlugin = async (_input: PluginInput = {}): Promise<PluginHooks> => {
  const tool: Record<string, HostTool> = {};
  for (const def of XTALK_TOOLS) {
    tool[def.id] = {
      description: def.description,
      args: def.inputSchema,
      parameters: def.inputSchema,
      execute: async (args: Record<string, unknown> = {}) => {
        const ctx: ToolContext = { env: process.env };
        return JSON.stringify(await runTool(def.name, args, ctx), null, 2);
      },
    };
  }
  return { tool };
};

export default CosmosXTalkPlugin;
