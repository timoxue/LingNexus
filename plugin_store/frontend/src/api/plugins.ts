export interface PluginStoreItem {
  plugin_id: string;
  display_name: string;
  version: string;
  description: string;
  tags: string[];
  enabled: boolean;
}

export interface PluginDetail {
  plugin_id: string;
  display_name: string;
  version: string;
  description: string;
  tags: string[];
  input_schema: {
    type: string;
    properties: Record<string, any>;
    required?: string[];
  };
  output_schema: {
    type: string;
    properties: Record<string, any>;
  };
  enabled: boolean;
}

export interface RunPluginRequest {
  payload: Record<string, any>;
}

export interface PluginInvokeResponse {
  status: string;
  output?: any;
  error?: string;
}

// 获取插件列表
export async function fetchPlugins(): Promise<PluginStoreItem[]> {
  const response = await fetch('/api/plugins');
  if (!response.ok) {
    throw new Error('Failed to fetch plugins');
  }
  return response.json();
}

// 获取插件详情
export async function fetchPluginDetail(pluginId: string): Promise<PluginDetail> {
  const response = await fetch(`/api/plugins/${pluginId}`);
  if (!response.ok) {
    throw new Error('Failed to fetch plugin detail');
  }
  return response.json();
}

// 运行插件
export async function runPlugin(pluginId: string, payload: Record<string, any>): Promise<PluginInvokeResponse> {
  const response = await fetch(`/api/plugins/${pluginId}/run`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ payload }),
  });
  if (!response.ok) {
    throw new Error('Failed to run plugin');
  }
  return response.json();
}
