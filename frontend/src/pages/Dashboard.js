import { useState, useEffect } from 'react';
import API from '../services/api';

function Dashboard({ onLogout }) {
  const [stats, setStats] = useState(null);
  const [products, setProducts] = useState([]);
  const [url, setUrl] = useState('');
  const [name, setName] = useState('');
  const [targetPrice, setTargetPrice] = useState('');
  const [message, setMessage] = useState('');
  const [selectedProduct, setSelectedProduct] = useState(null);
  const [history, setHistory] = useState([]);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const statsRes = await API.get('/products/dashboard/stats');
      setStats(statsRes.data);
      const productsRes = await API.get('/products/my-products');
      setProducts(productsRes.data);
    } catch (err) {
      console.error('Failed to load data');
    }
  };

  const handleTrack = async (e) => {
    e.preventDefault();
    try {
      await API.post('/products/track', {
        url: url,
        name: name,
        target_price: parseFloat(targetPrice) || null,
      });
      setMessage('Product added!');
      setUrl('');
      setName('');
      setTargetPrice('');
      loadData();
    } catch (err) {
      setMessage('Failed to add product');
    }
  };

  const handleCheckPrices = async () => {
    setMessage('Checking prices...');
    try {
      await API.post('/products/check-prices');
      setMessage('Prices checked!');
      loadData();
    } catch (err) {
      setMessage('Price check failed');
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    onLogout();
  };

  const viewHistory = async (product) => {
    if (selectedProduct?.id === product.id) {
      setSelectedProduct(null);
      setHistory([]);
      return;
    }
    try {
      const res = await API.get(`/products/${product.id}/history`);
      setHistory(res.data);
      setSelectedProduct(product);
    } catch (err) {
      console.error('Failed to load history');
    }
  };

  const stopTracking = async (productId) => {
    try {
      await API.delete(`/products/${productId}`);
      setMessage('Tracking stopped');
      setSelectedProduct(null);
      loadData();
    } catch (err) {
      setMessage('Failed to stop tracking');
    }
  };

  return (
    <div className="dashboard">
      <div className="header">
        <h1>Vastarion Hunter</h1>
        <button onClick={handleLogout} className="logout-btn">Logout</button>
      </div>

      {stats && (
        <div className="stats-grid">
          <div className="stat-card">
            <h3>{stats.total_products}</h3>
            <p>Total Products</p>
          </div>
          <div className="stat-card">
            <h3>{stats.active_products}</h3>
            <p>Active</p>
          </div>
          <div className="stat-card">
            <h3>{stats.deals_found}</h3>
            <p>Deals Found</p>
          </div>
        </div>
      )}

      <div className="track-form">
        <h2>Track New Product</h2>
        <form onSubmit={handleTrack}>
          <input
            type="url"
            placeholder="Product URL"
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            required
          />
          <input
            type="text"
            placeholder="Product Name"
            value={name}
            onChange={(e) => setName(e.target.value)}
            required
          />
          <input
            type="number"
            placeholder="Target Price (optional)"
            value={targetPrice}
            onChange={(e) => setTargetPrice(e.target.value)}
          />
          <button type="submit">Track Product</button>
        </form>
        {message && <p className="message">{message}</p>}
      </div>

      <div className="products-section">
        <div className="products-header">
          <h2>My Products</h2>
          <button onClick={handleCheckPrices} className="check-btn">Check Prices</button>
        </div>
        <div className="products-list">
          {products.map((product) => (
            <div key={product.id} className={`product-card ${selectedProduct?.id === product.id ? 'selected' : ''}`}>
              <div onClick={() => viewHistory(product)} className="product-clickable">
                <h3>{product.name}</h3>
                <p>Current: {product.current_price ? `${product.current_price} TL` : 'Not checked yet'}</p>
                <p>Target: {product.target_price ? `${product.target_price} TL` : 'No target'}</p>
                <span className={product.is_active ? 'active' : 'inactive'}>
                  {product.is_active ? 'Active' : 'Inactive'}
                </span>
              </div>

              {selectedProduct?.id === product.id && (
                <div className="history-panel">
                  <h4>Price History</h4>
                  {history.length > 0 ? (
                    <div className="history-list">
                      {history.map((h) => (
                        <div key={h.id} className="history-item">
                          <span>{h.price} TL</span>
                          <span className="history-date">
                            {new Date(h.checked_at).toLocaleDateString('tr-TR')}
                          </span>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <p className="no-history">No price history yet</p>
                  )}
                  <button onClick={() => stopTracking(product.id)} className="stop-btn">
                    Stop Tracking
                  </button>
                </div>
              )}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

export default Dashboard;