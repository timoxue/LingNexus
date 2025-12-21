import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { fetchPlugins } from '../api/plugins';
import type { PluginStoreItem } from '../api/plugins';

export const PluginList: React.FC = () => {
  const [plugins, setPlugins] = useState<PluginStoreItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadPlugins();
  }, []);

  const loadPlugins = async () => {
    try {
      setLoading(true);
      const data = await fetchPlugins();
      setPlugins(data);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div style={{ padding: '20px', textAlign: 'center' }}>
        <p>加载中...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div style={{ padding: '20px', color: 'red' }}>
        <p>错误: {error}</p>
        <button onClick={loadPlugins}>重试</button>
      </div>
    );
  }

  return (
    <div style={{ padding: '20px' }}>
      <h1>LingNexus Plugin Store</h1>
      <p style={{ color: '#666', marginBottom: '20px' }}>
        当前已安装 {plugins.length} 个插件
      </p>
      
      <div style={{ display: 'grid', gap: '15px' }}>
        {plugins.map((plugin) => (
          <Link
            key={plugin.plugin_id}
            to={`/plugin/${plugin.plugin_id}`}
            style={{ textDecoration: 'none', color: 'inherit' }}
          >
            <div
              style={{
                border: '1px solid #ddd',
                borderRadius: '8px',
                padding: '15px',
                cursor: 'pointer',
                transition: 'all 0.2s',
                backgroundColor: '#fff',
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.boxShadow = '0 2px 8px rgba(0,0,0,0.1)';
                e.currentTarget.style.borderColor = '#4CAF50';
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.boxShadow = 'none';
                e.currentTarget.style.borderColor = '#ddd';
              }}
            >
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start' }}>
                <div>
                  <h3 style={{ margin: '0 0 8px 0', color: '#333' }}>
                    {plugin.display_name}
                  </h3>
                  <p style={{ margin: '0 0 8px 0', color: '#666', fontSize: '14px' }}>
                    {plugin.description}
                  </p>
                  <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
                    {plugin.tags.map((tag) => (
                      <span
                        key={tag}
                        style={{
                          display: 'inline-block',
                          padding: '2px 8px',
                          backgroundColor: '#e8f5e9',
                          color: '#2e7d32',
                          borderRadius: '4px',
                          fontSize: '12px',
                        }}
                      >
                        {tag}
                      </span>
                    ))}
                  </div>
                </div>
                <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-end', gap: '8px' }}>
                  <span style={{ fontSize: '12px', color: '#999' }}>
                    v{plugin.version}
                  </span>
                  <span
                    style={{
                      padding: '4px 8px',
                      borderRadius: '4px',
                      fontSize: '12px',
                      backgroundColor: plugin.enabled ? '#4CAF50' : '#ccc',
                      color: '#fff',
                    }}
                  >
                    {plugin.enabled ? '已启用' : '已禁用'}
                  </span>
                </div>
              </div>
            </div>
          </Link>
        ))}
      </div>

      {plugins.length === 0 && (
        <div style={{ textAlign: 'center', padding: '40px', color: '#999' }}>
          <p>暂无可用插件</p>
        </div>
      )}
    </div>
  );
};
