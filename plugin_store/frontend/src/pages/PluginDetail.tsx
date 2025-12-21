import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { fetchPluginDetail, runPlugin } from '../api/plugins';
import type { PluginDetail } from '../api/plugins';

export const PluginDetailPage: React.FC = () => {
  const { pluginId } = useParams<{ pluginId: string }>();
  const navigate = useNavigate();
  
  const [plugin, setPlugin] = useState<PluginDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  
  const [formData, setFormData] = useState<Record<string, any>>({});
  const [running, setRunning] = useState(false);
  const [result, setResult] = useState<any>(null);

  useEffect(() => {
    if (pluginId) {
      loadPluginDetail(pluginId);
    }
  }, [pluginId]);

  const loadPluginDetail = async (id: string) => {
    try {
      setLoading(true);
      const data = await fetchPluginDetail(id);
      setPlugin(data);
      
      // 初始化表单数据
      const initialData: Record<string, any> = {};
      if (data.input_schema?.properties) {
        Object.keys(data.input_schema.properties).forEach((key) => {
          const prop = data.input_schema.properties[key];
          initialData[key] = prop.default || '';
        });
      }
      setFormData(initialData);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = (key: string, value: any) => {
    setFormData((prev) => ({ ...prev, [key]: value }));
  };

  const handleRun = async () => {
    if (!pluginId || !plugin) return;

    try {
      setRunning(true);
      setResult(null);
      const response = await runPlugin(pluginId, formData);
      setResult(response);
    } catch (err) {
      setResult({
        status: 'error',
        error: err instanceof Error ? err.message : 'Unknown error',
      });
    } finally {
      setRunning(false);
    }
  };

  const renderInputField = (key: string, schema: any) => {
    const value = formData[key] || '';
    const isRequired = plugin?.input_schema?.required?.includes(key);

    return (
      <div key={key} style={{ marginBottom: '15px' }}>
        <label style={{ display: 'block', marginBottom: '5px', fontWeight: 'bold' }}>
          {schema.description || key}
          {isRequired && <span style={{ color: 'red' }}> *</span>}
        </label>
        
        {schema.type === 'string' && schema.enum ? (
          <select
            value={value}
            onChange={(e) => handleInputChange(key, e.target.value)}
            style={{
              width: '100%',
              padding: '8px',
              borderRadius: '4px',
              border: '1px solid #ddd',
            }}
          >
            <option value="">请选择</option>
            {schema.enum.map((option: string) => (
              <option key={option} value={option}>
                {option}
              </option>
            ))}
          </select>
        ) : schema.type === 'array' ? (
          <textarea
            value={Array.isArray(value) ? value.join('\n') : value}
            onChange={(e) => handleInputChange(key, e.target.value.split('\n').filter(Boolean))}
            placeholder="每行一个值"
            rows={4}
            style={{
              width: '100%',
              padding: '8px',
              borderRadius: '4px',
              border: '1px solid #ddd',
              fontFamily: 'monospace',
            }}
          />
        ) : schema.type === 'boolean' ? (
          <input
            type="checkbox"
            checked={Boolean(value)}
            onChange={(e) => handleInputChange(key, e.target.checked)}
            style={{ width: '20px', height: '20px' }}
          />
        ) : (
          <input
            type="text"
            value={value}
            onChange={(e) => handleInputChange(key, e.target.value)}
            placeholder={schema.description || ''}
            style={{
              width: '100%',
              padding: '8px',
              borderRadius: '4px',
              border: '1px solid #ddd',
            }}
          />
        )}
        
        {schema.examples && (
          <small style={{ color: '#999', marginTop: '5px', display: 'block' }}>
            示例: {JSON.stringify(schema.examples)}
          </small>
        )}
      </div>
    );
  };

  if (loading) {
    return (
      <div style={{ padding: '20px', textAlign: 'center' }}>
        <p>加载中...</p>
      </div>
    );
  }

  if (error || !plugin) {
    return (
      <div style={{ padding: '20px' }}>
        <p style={{ color: 'red' }}>错误: {error || '插件未找到'}</p>
        <button onClick={() => navigate('/')}>返回列表</button>
      </div>
    );
  }

  return (
    <div style={{ padding: '20px', maxWidth: '800px', margin: '0 auto' }}>
      <button
        onClick={() => navigate('/')}
        style={{
          marginBottom: '20px',
          padding: '8px 16px',
          cursor: 'pointer',
          border: '1px solid #ddd',
          borderRadius: '4px',
          backgroundColor: '#fff',
        }}
      >
        ← 返回列表
      </button>

      <div style={{ marginBottom: '30px' }}>
        <h1>{plugin.display_name}</h1>
        <p style={{ color: '#666' }}>{plugin.description}</p>
        <div style={{ display: 'flex', gap: '10px', marginTop: '10px' }}>
          <span style={{ fontSize: '14px', color: '#999' }}>v{plugin.version}</span>
          {plugin.tags.map((tag) => (
            <span
              key={tag}
              style={{
                padding: '4px 8px',
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

      <div
        style={{
          border: '1px solid #ddd',
          borderRadius: '8px',
          padding: '20px',
          backgroundColor: '#f9f9f9',
          marginBottom: '20px',
        }}
      >
        <h3 style={{ marginTop: 0 }}>输入参数</h3>
        {plugin.input_schema?.properties &&
          Object.entries(plugin.input_schema.properties).map(([key, schema]) =>
            renderInputField(key, schema)
          )}

        <button
          onClick={handleRun}
          disabled={running || !plugin.enabled}
          style={{
            width: '100%',
            padding: '12px',
            marginTop: '15px',
            backgroundColor: plugin.enabled ? '#4CAF50' : '#ccc',
            color: '#fff',
            border: 'none',
            borderRadius: '4px',
            cursor: plugin.enabled ? 'pointer' : 'not-allowed',
            fontSize: '16px',
            fontWeight: 'bold',
          }}
        >
          {running ? '运行中...' : plugin.enabled ? '运行插件' : '插件已禁用'}
        </button>
      </div>

      {result && (
        <div
          style={{
            border: '1px solid #ddd',
            borderRadius: '8px',
            padding: '20px',
            backgroundColor: result.status === 'success' ? '#e8f5e9' : '#ffebee',
          }}
        >
          <h3 style={{ marginTop: 0 }}>
            执行结果: {result.status === 'success' ? '✅ 成功' : '❌ 失败'}
          </h3>
          <pre
            style={{
              backgroundColor: '#fff',
              padding: '15px',
              borderRadius: '4px',
              overflow: 'auto',
              fontSize: '14px',
            }}
          >
            {JSON.stringify(result, null, 2)}
          </pre>
        </div>
      )}
    </div>
  );
};
