/*
Finalized interactive preview for "True Religion Of Zion" with:
- Branded nav, hero, resources, donate, shop pages
- Real hero & merch images (royalty-free placeholders included)
- Admin Upload page to upload PDFs (stored in-memory, preview)
- Download after donation simulation ($20 minimum)
*/

import React, { useMemo, useState, createContext, useContext } from 'react';
import { BrowserRouter as Router, Routes, Route, Link, useLocation, useNavigate } from 'react-router-dom';
import './App.css';

const brand = {
  name: 'True Religion Of Zion',
  primary: '#2E4D37',
  secondary: '#BF9B30',
  accent: '#E4D6A7',
  font: 'Playfair Display, serif',
};

const heroImages = [
  { alt: 'Native / Indigenous family studying', src: '/media/hero/native.jpg' },
  { alt: 'African American elders reading scripture', src: '/media/hero/african-american.jpg' },
  { alt: 'Afro‑Latino couple discussing study notes', src: '/media/hero/afro-latino.jpg' },
  { alt: 'Pacific Islander brothers fellowshipping', src: '/media/hero/pacific-islander.jpg' },
  { alt: 'Caribbean islanders in group discussion', src: '/media/hero/caribbean.jpg' },
];

const productsSeed = [
  { id: 'p1', name: 'Gentiles Study Tee', price: 25, alt: 'Native model wearing tee', img: '/media/merch/gentiles-tee-native.jpg' },
  { id: 'p2', name: 'Sabbath Mug', price: 15, alt: 'Afro‑Latino hand with mug', img: '/media/merch/sabbath-mug-afrolatino.jpg' },
  { id: 'p3', name: 'Context Hoodie', price: 45, alt: 'Pacific Islander model hoodie', img: '/media/merch/context-hoodie-pacific.jpg' },
];

const ResourceContext = createContext(null);
const useResources = () => useContext(ResourceContext);

function ResourceProvider({ children }) {
  const [resources, setResources] = useState([
    { id: 'r1', title: 'Who Are the Gentiles?', category: 'Bible Study', blurb: 'Ethnos in context: scattered Israelites living as nations.', cover: '/media/covers/gentiles.png', path: '/resources/gentiles.pdf' },
    { id: 'r2', title: 'Law of Sin & Death (Romans 8:2)', category: 'Bible Study', blurb: 'Sacrifice vs. the whole law—grace from immediate judgment.', cover: '/media/covers/law-of-sin.png', path: '/resources/law-of-sin.pdf' },
    { id: 'r3', title: 'Christ’s Birth: Joseph vs. Immaculate', category: 'Bible Study', blurb: 'Genealogy, marriage law, and first‑century context.', cover: '/media/covers/christ-birth.png', path: '/resources/christ-birth.pdf' },
  ]);
  const addResource = (res) => setResources(prev => [res, ...prev]);
  return <ResourceContext.Provider value={{ resources, addResource }}>{children}</ResourceContext.Provider>;
}

function useActive(path) {
  const { pathname } = useLocation();
  return pathname === path;
}

const Button = ({ to, onClick, children, variant = 'solid' }) => {
  const base = { padding: '0.75rem 1.25rem', borderRadius: 12, fontWeight: 700, transition: 'all .2s ease', display: 'inline-block' };
  const styles = variant === 'solid' ? { background: brand.secondary, color: 'white' } : { border: `2px solid ${brand.secondary}`, color: brand.secondary };
  const hover = variant === 'solid' ? { filter: 'brightness(0.9)' } : { background: brand.secondary, color: 'white' };
  const content = <span style={{ ...base, ...styles }} className="btn" onMouseEnter={e=>Object.assign(e.currentTarget.style, hover)} onMouseLeave={e=>Object.assign(e.currentTarget.style, styles)}>{children}</span>;
  return to ? <Link to={to}>{content}</Link> : <button onClick={onClick} style={{ border: 'none', background: 'transparent', padding: 0 }}>{content}</button>;
};

const Card = ({ children, onClick }) => <div onClick={onClick} className="rounded-2xl p-4 shadow-sm border hover:shadow-md transition cursor-pointer bg-white" style={{ borderColor: '#eee' }}>{children}</div>;

const Header = () => {
  const navItems = [
    { path: '/', label: 'Home' },
    { path: '/resources', label: 'Resources' },
    { path: '/shop', label: 'Shop' },
    { path: '/donate', label: 'Donate' },
    { path: '/admin-upload', label: 'Admin Upload' },
  ];
  return (
    <header className="sticky top-0 bg-white z-50" style={{ boxShadow: '0 1px 10px rgba(0,0,0,.05)' }}>
      <div className="max-w-6xl mx-auto flex items-center justify-between p-4" style={{ fontFamily: brand.font }}>
        <Link to="/" className="font-bold text-2xl" style={{ color: brand.primary }}>{brand.name}</Link>
        <nav className="flex gap-4 text-sm">
          {navItems.map(n => {
            const active = useActive(n.path);
            return <Link key={n.path} to={n.path} className={`px-2 py-1 rounded ${active ? 'bg-gray-100' : ''}`}>{n.label}</Link>;
          })}
        </nav>
      </div>
    </header>
  );
};

const Footer = () => <footer className="mt-16 py-8 bg-gray-50 text-center text-sm text-gray-600">© {new Date().getFullYear()} {brand.name}. All rights reserved.</footer>;

const Home = () => {
  const navigate = useNavigate();
  const { resources } = useResources();
  return (
    <>
      <section className="max-w-6xl mx-auto px-4" style={{ fontFamily: brand.font }}>
        <div className="grid md:grid-cols-2 gap-8 items-center py-10">
          <div>
            <h1 className="text-4xl md:text-5xl font-bold mb-4" style={{ color: brand.primary }}>Read Scripture in Context</h1>
            <p className="text-lg text-gray-700 mb-6">Israelite-centered studies with precepts, Septuagint + Apocrypha references, and historical documents—all in one place.</p>
            <div className="flex flex-wrap gap-3">
              <Button to="/resources">Explore Resources</Button>
              <Button to="/donate" variant="outline">Donate & Download</Button>
            </div>
          </div>
          <div className="grid grid-cols-3 gap-2">
            {heroImages.map((img, i) => (
              <div key={i} className="rounded-2xl aspect-square overflow-hidden bg-gray-100">
                <img src={img.src} alt={img.alt} className="w-full h-full object-cover" />
              </div>
            ))}
          </div>
        </div>
      </section>
      <section className="max-w-6xl mx-auto px-4 py-8">
        <div className="flex items-end justify-between mb-4"><h2 className="text-2xl font-bold" style={{ color: brand.primary }}>Featured Resources</h2><Link to="/resources" className="text-sm" style={{ color: brand.secondary }}>View all →</Link></div>
        <div className="grid sm:grid-cols-2 md:grid-cols-3 gap-4">
          {resources.slice(0,3).map(r => (
            <Card key={r.id} onClick={()=>navigate('/resources')}>
              <div className="rounded-xl mb-3 w-full aspect-[3/4] overflow-hidden bg-gray-100">{r.cover ? <img src={r.cover} alt={r.title} className="w-full h-full object-cover" /> : <div className="w-full h-full flex items-center justify-center text-xs text-gray-500">No cover</div>}</div>
              <div className="text-xs uppercase tracking-wide text-gray-500">{r.category}</div>
              <div className="font-semibold">{r.title}</div>
              <p className="text-sm text-gray-600 mt-1">{r.blurb}</p>
            </Card>
          ))}
        </div>
      </section>
      <section className="max-w-6xl mx-auto px-4 py-8">
        <div className="flex items-end justify-between mb-4"><h2 className="text-2xl font-bold" style={{ color: brand.primary }}>Merchandise</h2><Link to="/shop" className="text-sm" style={{ color: brand.secondary }}>Shop all →</Link></div>
        <div className="grid sm:grid-cols-2 md:grid-cols-3 gap-4">
          {productsSeed.map(p => (
            <Card key={p.id} onClick={()=>navigate('/shop')}>
              <div className="rounded-xl mb-3 w-full aspect-video overflow-hidden bg-gray-100"><img src={p.img} alt={p.alt} className="w-full h-full object-cover" /></div>
              <div className="font-semibold">{p.name}</div>
              <div className="text-sm text-gray-700">${p.price}</div>
            </Card>
          ))}
        </div>
      </section>
    </>
  );
};

const Resources = () => {
  const { resources } = useResources();
  const [category, setCategory] = useState('All');
  const categories = useMemo(() => ['All', ...Array.from(new Set(resources.map(r => r.category)))], [resources]);
  const list = useMemo(() => resources.filter(r => category === 'All' ? true : r.category === category), [category, resources]);
  const navigate = useNavigate();
  return (
    <section className="max-w-6xl mx-auto px-4" style={{ fontFamily: brand.font }}>
      <div className="flex items-center justify-between py-6"><div><h1 className="text-3xl font-bold" style={{ color: brand.primary }}>Resources</h1><p className="text-gray-700">Donate $20+ to download.</p></div><div className="flex items-center gap-2"><span className="text-sm">Category</span><select className="border rounded px-2 py-1" value={category} onChange={e=>setCategory(e.target.value)}>{categories.map(c => <option key={c}>{c}</option>)}</select></div></div>
      <div className="grid sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
        {list.map(r => (
          <Card key={r.id} onClick={()=>navigate(`/donate?id=${r.id}`)}>
            <div className="rounded-xl mb-3 w-full aspect-[3/4] overflow-hidden bg-gray-100">{r.cover ? <img src={r.cover} alt={r.title} className="w-full h-full object-cover" /> : <div className="w-full h-full flex items-center justify-center text-xs text-gray-500">No cover</div>}</div>
            <div className="text-xs uppercase tracking-wide text-gray-500">{r.category}</div>
            <div className="font-semibold">{r.title}</div>
            <p className="text-sm text-gray-600 mt-1 mb-3">{r.blurb}</p>
            <Button to={`/donate?id=${r.id}`}>Donate & Download</Button>
          </Card>
        ))}
      </div>
      <div className="mt-6 text-sm text-gray-600">Admin? <Link to="/admin-upload" className="text-blue-600">Upload a resource</Link></div>
    </section>
  );
};

const Donate = () => {
  const { resources } = useResources();
  const params = new URLSearchParams(window.location.search);
  const pre = params.get('id') || 'r1';
  const [selected, setSelected] = useState(pre);
  const [amount, setAmount] = useState(20);
  const [email, setEmail] = useState('');
  const [error, setError] = useState('');
  const handleSubmit = (e) => {
    e.preventDefault();
    setError('');
    if (amount < 20) return setError('Minimum donation is $20 to download.');
    if (!email) return setError('Please enter an email for the receipt.');
    const item = resources.find(r=>r.id===selected);
    if (item && item.path) {
      alert('Demo: Payment flow would start here. After success, the download begins.');
      const a = document.createElement('a');
      a.href = item.path;
      a.download = item.title.replace(/\s+/g,'-').toLowerCase() + '.pdf';
      document.body.appendChild(a); a.click(); a.remove();
    } else alert('No file available');
  };
  return (
    <section className="max-w-md mx-auto px-4 py-8" style={{ fontFamily: brand.font }}>
      <h1 className="text-3xl font-bold mb-4" style={{ color: brand.primary }}>Donate & Download</h1>
      <form onSubmit={handleSubmit} className="space-y-3">
        <label className="block text-sm">Select Resource</label>
        <select className="border rounded px-2 py-2 w-full" value={selected} onChange={e=>setSelected(e.target.value)}>{resources.map(r => <option key={r.id} value={r.id}>{r.title} — {r.category}</option>)}</select>
        <label className="block text-sm">Donation Amount (USD)</label>
        <input type="number" min={20} className="border rounded px-2 py-2 w-full" value={amount} onChange={e=>setAmount(Number(e.target.value))} />
        <label className="block text-sm">Email</label>
        <input type="email" className="border rounded px-2 py-2 w-full" value={email} onChange={e=>setEmail(e.target.value)} placeholder="you@example.com" />
        {error && <div className="text-red-600 text-sm">{error}</div>}
        <div className="pt-2"><Button>Donate & Download (Demo)</Button></div>
      </form>
    </section>
  );
};

const Shop = () => (
  <section className="max-w-6xl mx-auto px-4" style={{ fontFamily: brand.font }}>
    <div className="py-6"><h1 className="text-3xl font-bold" style={{ color: brand.primary }}>Shop</h1><p className="text-gray-700">Preview of merch items (demo).</p></div>
    <div className="grid sm:grid-cols-2 md:grid-cols-3 gap-4">{productsSeed.map(p => (<Card key={p.id}><div className="rounded-xl mb-3 w-full aspect-video overflow-hidden bg-gray-100"><img src={p.img} alt={p.alt} className="w-full h-full object-cover" /></div><div className="font-semibold">{p.name}</div><div className="text-sm text-gray-700 mb-3">${p.price}</div><Button variant="outline">Add to Cart (Demo)</Button></Card>))}</div>
  </section>
);

const AdminUpload = () => {
  const { addResource } = useResources();
  const [title, setTitle] = useState('');
  const [category, setCategory] = useState('Bible Study');
  const [blurb, setBlurb] = useState('');
  const [file, setFile] = useState(null);
  const handleSubmit = (e) => {
    e.preventDefault();
    if (!title || !file) return alert('Title and PDF required');
    const id = 'r' + Math.random().toString(36).slice(2,7);
    const path = URL.createObjectURL(file);
    addResource({ id, title, category, blurb, cover: null, path });
    alert('Resource added for this session.');
    setTitle(''); setCategory('Bible Study'); setBlurb(''); setFile(null);
  };
  return (
    <section className="max-w-xl mx-auto px-4 py-8" style={{ fontFamily: brand.font }}>
      <h1 className="text-3xl font-bold mb-4" style={{ color: brand.primary }}>Admin Upload (Demo)</h1>
      <form onSubmit={handleSubmit} className="space-y-3">
        <label className="block text-sm">Title</label>
        <input className="border rounded px-2 py-2 w-full" value={title} onChange={e=>setTitle(e.target.value)} />
        <label className="block text-sm">Category</label>
        <select className="border rounded px-2 py-2 w-full" value={category} onChange={e=>setCategory(e.target.value)}>
          {['Bible Study','Historical Document','Historical Reference','Teaching Aid','Other'].map(c=> <option key={c}>{c}</option>)}
        </select>
        <label className="block text-sm">Short description (optional)</label>
        <input className="border rounded px-2 py-2 w-full" value={blurb} onChange={e=>setBlurb(e.target.value)} placeholder="One‑line blurb for the card" />
        <label className="block text-sm">PDF File</label>
        <input type="file" accept="application/pdf" onChange={e=>setFile(e.target.files?.[0] || null)} className="border rounded px-2 py-2 w-full" />
        <div className="pt-2"><Button>Upload (Demo)</Button></div>
      </form>
    </section>
  );
};

const Layout = ({ children }) => (
  <div style={{ fontFamily: brand.font }}>
    <Header />
    {children}
    <Footer />
  </div>
);

export default function App() {
  return (
    <Router>
      <ResourceProvider>
        <Layout>
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/resources" element={<Resources />} />
            <Route path="/donate" element={<Donate />} />
            <Route path="/shop" element={<Shop />} />
            <Route path="/admin-upload" element={<AdminUpload />} />
          </Routes>
        </Layout>
      </ResourceProvider>
    </Router>
  );
}
