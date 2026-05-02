# New template functions for the expanded marketplace
# Injected into generator.py via _inject_new_templates.py


def _mv_about_html(site_name: str) -> str:
    return f"""{{% extends 'base.html' %}}
{{% block title %}}About — {site_name}{{% endblock %}}
{{% block content %}}
<div class="mv-dash" style="max-width:900px;margin:0 auto">
  <div style="text-align:center;padding:3rem 1rem 2rem">
    <h1 style="font-size:2rem;font-weight:800;margin-bottom:.75rem">About <span style="color:var(--mv-pink)">{site_name}</span></h1>
    <p style="color:#666;font-size:1.05rem;max-width:600px;margin:0 auto">
      {site_name} is India's fastest-growing multi-vendor marketplace, connecting millions of sellers with customers across the country.
    </p>
  </div>
  <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:1.5rem;margin-bottom:3rem">
    <div class="mv-stat" style="border-top:4px solid var(--mv-pink)">
      <div class="mv-stat-val">{{{{ stats.sellers }}}}+</div>
      <div class="mv-stat-label">Active Sellers</div>
    </div>
    <div class="mv-stat" style="border-top:4px solid #ff5722">
      <div class="mv-stat-val">{{{{ stats.products }}}}+</div>
      <div class="mv-stat-label">Products Listed</div>
    </div>
    <div class="mv-stat" style="border-top:4px solid #4caf50">
      <div class="mv-stat-val">{{{{ stats.orders }}}}+</div>
      <div class="mv-stat-label">Orders Delivered</div>
    </div>
  </div>
  <div style="display:grid;grid-template-columns:1fr 1fr;gap:2rem;margin-bottom:3rem">
    <div style="background:#fff;border-radius:16px;padding:2rem;box-shadow:0 2px 8px rgba(0,0,0,.06)">
      <h3 style="font-weight:800;margin-bottom:.75rem">🎯 Our Mission</h3>
      <p style="color:#666;line-height:1.7">To empower every seller — from home entrepreneurs to established businesses — with the tools to reach millions of customers and grow their income.</p>
    </div>
    <div style="background:#fff;border-radius:16px;padding:2rem;box-shadow:0 2px 8px rgba(0,0,0,.06)">
      <h3 style="font-weight:800;margin-bottom:.75rem">💡 Our Vision</h3>
      <p style="color:#666;line-height:1.7">A marketplace where quality products from every corner of India are accessible to every customer, at the best prices, with zero friction.</p>
    </div>
  </div>
  <div style="text-align:center;padding:2rem;background:linear-gradient(135deg,var(--mv-pink),#ff5722);border-radius:16px;color:#fff">
    <h2 style="font-weight:800;margin-bottom:.5rem">Want to sell on {site_name}?</h2>
    <p style="opacity:.9;margin-bottom:1.25rem">Join thousands of sellers already earning on our platform.</p>
    <a href="{{{{ url_for('become_supplier') }}}}" style="background:#fff;color:var(--mv-pink);padding:.7rem 2rem;border-radius:30px;font-weight:700;text-decoration:none">Become a Seller</a>
  </div>
</div>
{{% endblock %}}"""


def _mv_deals_html() -> str:
    return """{%- extends 'base.html' %}
{%- block title %}Deals of the Day{%- endblock %}
{%- block content %}
<div style="max-width:1400px;margin:0 auto;padding:1.5rem">
  <div style="display:flex;align-items:center;gap:.75rem;margin-bottom:1.5rem">
    <span style="font-size:1.8rem">🔥</span>
    <h2 style="font-size:1.5rem;font-weight:800;margin:0">Deals of the Day</h2>
    <span style="background:#ffebee;color:#e91e63;padding:.2rem .75rem;border-radius:20px;font-size:.82rem;font-weight:700">Up to 80% OFF</span>
  </div>
  {%- if products %}
  <div class="mv-grid">
    {%- for p in products %}
    <div class="mv-card" onclick="location.href='{{ url_for('product_detail', pid=p.id) }}'">
      <div style="position:relative">
        <img src="{{ url_for('static', filename='uploads/' + (p.image or 'default.png')) }}"
             alt="{{ p.name }}" onerror="this.src='https://placehold.co/300x300/fce4ec/e91e63?text=No+Image'"/>
        <span style="position:absolute;top:8px;left:8px;background:#e91e63;color:#fff;padding:.2rem .6rem;border-radius:20px;font-size:.72rem;font-weight:700">
          {{ p.discount_percent|int }}% OFF
        </span>
      </div>
      <div class="mv-card-body">
        <div class="mv-card-name">{{ p.name }}</div>
        <div style="display:flex;align-items:center;gap:.5rem">
          <div class="mv-card-price">₹{{ '%.0f'|format(p.price) }}</div>
          {%- if p.mrp and p.mrp > p.price %}
          <div style="font-size:.78rem;color:#888;text-decoration:line-through">₹{{ '%.0f'|format(p.mrp) }}</div>
          {%- endif %}
        </div>
        {%- if session.role == 'customer' or not session.role %}
        <form method="POST" action="{{ url_for('add_to_cart', pid=p.id) }}" onclick="event.stopPropagation()">
          <input type="hidden" name="quantity" value="1"/>
          <button type="submit" class="mv-card-btn">Add to Cart</button>
        </form>
        {%- endif %}
      </div>
    </div>
    {%- endfor %}
  </div>
  {%- else %}
  <div style="text-align:center;padding:4rem 1rem">
    <div style="font-size:4rem">🏷️</div>
    <h3 style="margin:.75rem 0;color:#555">No deals right now</h3>
    <p style="color:#888">Check back soon for amazing offers!</p>
    <a href="{{ url_for('index') }}" class="mv-btn mv-btn-primary" style="display:inline-block;margin-top:1rem">Browse All Products</a>
  </div>
  {%- endif %}
</div>
{%- endblock %}"""


def _mv_new_arrivals_html() -> str:
    return """{%- extends 'base.html' %}
{%- block title %}New Arrivals{%- endblock %}
{%- block content %}
<div style="max-width:1400px;margin:0 auto;padding:1.5rem">
  <div style="display:flex;align-items:center;gap:.75rem;margin-bottom:1.5rem">
    <span style="font-size:1.8rem">✨</span>
    <h2 style="font-size:1.5rem;font-weight:800;margin:0">New Arrivals</h2>
    <span style="background:#e8f5e9;color:#2e7d32;padding:.2rem .75rem;border-radius:20px;font-size:.82rem;font-weight:700">Just In</span>
  </div>
  {%- if products %}
  <div class="mv-grid">
    {%- for p in products %}
    <div class="mv-card" onclick="location.href='{{ url_for('product_detail', pid=p.id) }}'">
      <div style="position:relative">
        <img src="{{ url_for('static', filename='uploads/' + (p.image or 'default.png')) }}"
             alt="{{ p.name }}" onerror="this.src='https://placehold.co/300x300/fce4ec/e91e63?text=No+Image'"/>
        <span style="position:absolute;top:8px;left:8px;background:#4caf50;color:#fff;padding:.2rem .6rem;border-radius:20px;font-size:.72rem;font-weight:700">NEW</span>
      </div>
      <div class="mv-card-body">
        <div class="mv-card-name">{{ p.name }}</div>
        <div class="mv-card-price">₹{{ '%.0f'|format(p.price) }}</div>
        {%- if session.role == 'customer' or not session.role %}
        <form method="POST" action="{{ url_for('add_to_cart', pid=p.id) }}" onclick="event.stopPropagation()">
          <input type="hidden" name="quantity" value="1"/>
          <button type="submit" class="mv-card-btn">Add to Cart</button>
        </form>
        {%- endif %}
      </div>
    </div>
    {%- endfor %}
  </div>
  {%- else %}
  <div style="text-align:center;padding:4rem 1rem">
    <div style="font-size:4rem">📦</div>
    <h3 style="margin:.75rem 0;color:#555">No new arrivals yet</h3>
    <a href="{{ url_for('index') }}" class="mv-btn mv-btn-primary" style="display:inline-block;margin-top:1rem">Browse All Products</a>
  </div>
  {%- endif %}
</div>
{%- endblock %}"""
