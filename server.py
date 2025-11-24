from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from time import strftime, gmtime
from typing import List, Dict, Any
from plugins.database import Database

app = FastAPI(title="Bot Taxi Admin")
db = Database()

try:
    app.mount("/styles", StaticFiles(directory="table/styles"), name="styles")
except:
    pass


def row_to_dict(row) -> dict:
    if row is None:
        return {}
    if isinstance(row, dict):
        return row
    return {key: row[key] for key in row.keys()}


@app.get("/api/drivers")
async def api_get_drivers():
    drivers = await db.driver.admin_get_all()
    result = []
    for driver in drivers:
        d = row_to_dict(driver)
        try:
            d['first_activity'] = strftime("%c", gmtime(float(d['first_activity'])))
            d['last_activity'] = strftime("%c", gmtime(float(d['last_activity'])))
        except:
            pass
        result.append(d)
    return result


@app.get("/api/passangers")
async def api_get_passangers():
    passangers = [row_to_dict(record) async for record in db.passanger.admin_get_all()]
    return passangers


@app.get("/api/orders")
@app.get("/api/orders")
async def api_get_orders():
    from aiofiles import open as aiopen
    try:
        async with aiopen('cache/forms.json', 'r', encoding='utf-8') as file:
            content = await file.read()
            forms = eval(content) if content.strip() else {}
    except FileNotFoundError:
        forms = {}

    orders = []
    for key, data in forms.items():
        order_data = data.get('data', {})

        if isinstance(order_data, dict):
            location = order_data.get('location', [])
            location_str = ', '.join(map(str, location)) if location else ''
        else:
            location_str = ''

        orders.append({
            'key': key,
            'from_id': data.get('from_id', 0),
            'driver_id': data.get('driver_id', 0),
            'active': data.get('active', False),
            'in_drive': data.get('in_drive', False),
            'location': location_str
        })
    return orders


@app.get("/drivers", response_class=HTMLResponse)
async def get_drivers_page():
    drivers = await api_get_drivers()

    rows = ""
    for i, driver in enumerate(drivers):
        css_class = "tg-pvec" if i % 2 == 0 else "tg-ku2z"
        rows += f"""<tr>
            <td class="{css_class}">{driver.get('VK', '')}</td>
            <td class="{css_class}">{driver.get('status', '')}</td>
            <td class="{css_class}">{driver.get('gender', '')}</td>
            <td class="{css_class}">{driver.get('city', '')}</td>
            <td class="{css_class}">{driver.get('name', '')}</td>
            <td class="{css_class}">{driver.get('phone', '')}</td>
            <td class="{css_class}">{driver.get('auto', '')}</td>
            <td class="{css_class}">{driver.get('color', '')}</td>
            <td class="{css_class}">{driver.get('state_number', '')}</td>
            <td class="{css_class}">{driver.get('first_activity', '')}</td>
            <td class="{css_class}">{driver.get('last_activity', '')}</td>
            <td class="{css_class}">{driver.get('quantity', '')}</td>
            <td class="{css_class}">{driver.get('balance', '')}</td>
        </tr>"""

    html = Path('table/drivers.html').read_text(encoding='utf-8')
    return html.replace('{table}', rows)


@app.get("/passangers", response_class=HTMLResponse)
async def get_passangers_page():
    passangers = await api_get_passangers()

    rows = ""
    for i, passanger in enumerate(passangers):
        css_class = "tg-pvec" if i % 2 == 0 else "tg-ku2z"
        rows += f"""<tr>
            <td class="{css_class}">{passanger.get('VK', '')}</td>
            <td class="{css_class}">{passanger.get('gender', '')}</td>
            <td class="{css_class}">{passanger.get('city', '')}</td>
            <td class="{css_class}">{passanger.get('name', '')}</td>
            <td class="{css_class}">{passanger.get('phone', '')}</td>
            <td class="{css_class}">{passanger.get('quantity', '')}</td>
            <td class="{css_class}">{passanger.get('balance', '')}</td>
        </tr>"""

    html = Path('table/passangers.html').read_text(encoding='utf-8')
    return html.replace('{table}', rows)


@app.get("/orders", response_class=HTMLResponse)
async def get_orders_page():
    orders = await api_get_orders()

    rows = ""
    for i, order in enumerate(orders):
        css_class = "tg-pvec" if i % 2 == 0 else "tg-ku2z"
        rows += f"""<tr>
            <td class="{css_class}">{order['key']}</td>
            <td class="{css_class}">{order['from_id']}</td>
            <td class="{css_class}">{order['driver_id']}</td>
            <td class="{css_class}">{order['active']}</td>
            <td class="{css_class}">{order['in_drive']}</td>
            <td class="{css_class}">{order['location']}</td>
        </tr>"""

    html = Path('table/orders.html').read_text(encoding='utf-8')
    return html.replace('{table}', rows)


@app.get("/", response_class=HTMLResponse)
async def admin_dashboard():
    return """
    <!DOCTYPE html>
    <html lang="ru">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Bot Taxi Admin</title>
        <script src="https://cdn.jsdelivr.net/npm/vue@3/dist/vue.global.js"></script>
        <script src="https://cdn.jsdelivr.net/npm/axios/dist/axios.min.js"></script>
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body { 
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif;
                background: #f5f5f5;
                padding: 20px;
            }
            .container { max-width: 1400px; margin: 0 auto; }
            .header {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                padding: 30px;
                border-radius: 12px;
                margin-bottom: 20px;
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
                color: white;
            }
            .header h1 { font-size: 28px; font-weight: 600; }
            .stats {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
                gap: 20px;
                margin-bottom: 20px;
            }
            .stat-card {
                background: white;
                padding: 24px;
                border-radius: 12px;
                box-shadow: 0 2px 8px rgba(0,0,0,0.08);
                transition: transform 0.2s;
            }
            .stat-card:hover { transform: translateY(-2px); box-shadow: 0 4px 12px rgba(0,0,0,0.12); }
            .stat-card h3 { color: #666; font-size: 13px; margin-bottom: 12px; text-transform: uppercase; letter-spacing: 0.5px; }
            .stat-card .number { font-size: 36px; font-weight: 700; color: #667eea; }
            .tabs {
                display: flex;
                gap: 10px;
                margin-bottom: 20px;
                flex-wrap: wrap;
            }
            .tab {
                padding: 12px 24px;
                background: white;
                border: 2px solid transparent;
                border-radius: 8px;
                cursor: pointer;
                font-size: 14px;
                font-weight: 500;
                transition: all 0.2s;
                color: #333;
            }
            .tab:hover { background: #f8f8f8; border-color: #667eea; }
            .tab.active { background: #667eea; color: white; border-color: #667eea; }
            .content {
                background: white;
                padding: 24px;
                border-radius: 12px;
                box-shadow: 0 2px 8px rgba(0,0,0,0.08);
                overflow-x: auto;
            }
            .search {
                margin-bottom: 20px;
                padding: 12px 16px;
                width: 100%;
                max-width: 400px;
                border: 2px solid #e0e0e0;
                border-radius: 8px;
                font-size: 14px;
                transition: border-color 0.2s;
            }
            .search:focus { outline: none; border-color: #667eea; }
            table {
                width: 100%;
                border-collapse: collapse;
                min-width: 800px;
            }
            th {
                background: #f8f9fa;
                color: #333;
                padding: 14px 12px;
                text-align: left;
                font-weight: 600;
                font-size: 13px;
                text-transform: uppercase;
                letter-spacing: 0.5px;
                border-bottom: 2px solid #e0e0e0;
            }
            td {
                padding: 14px 12px;
                border-bottom: 1px solid #f0f0f0;
                color: #555;
                font-size: 14px;
            }
            tr:hover { background: #fafafa; }
            .loading {
                text-align: center;
                padding: 40px;
                color: #999;
            }
            .error {
                background: #fee;
                color: #c33;
                padding: 16px;
                border-radius: 8px;
                margin-bottom: 20px;
            }
        </style>
    </head>
    <body>
        <div id="app">
            <div class="container">
                <div class="header">
                    <h1>🚕 Bot Taxi Admin Panel</h1>
                </div>

                <div class="stats">
                    <div class="stat-card">
                        <h3>Водителей</h3>
                        <div class="number">{{ drivers.length }}</div>
                    </div>
                    <div class="stat-card">
                        <h3>Пассажиров</h3>
                        <div class="number">{{ passangers.length }}</div>
                    </div>
                    <div class="stat-card">
                        <h3>Активных заказов</h3>
                        <div class="number">{{ activeOrders }}</div>
                    </div>
                    <div class="stat-card">
                        <h3>Всего поездок</h3>
                        <div class="number">{{ totalTrips }}</div>
                    </div>
                </div>

                <div v-if="error" class="error">{{ error }}</div>

                <div class="tabs">
                    <button class="tab" :class="{active: tab === 'drivers'}" @click="tab = 'drivers'">
                        Водители ({{ drivers.length }})
                    </button>
                    <button class="tab" :class="{active: tab === 'passangers'}" @click="tab = 'passangers'">
                        Пассажиры ({{ passangers.length }})
                    </button>
                    <button class="tab" :class="{active: tab === 'orders'}" @click="tab = 'orders'">
                        Заказы ({{ orders.length }})
                    </button>
                </div>

                <div class="content">
                    <input 
                        v-model="search" 
                        class="search" 
                        placeholder="🔍 Поиск..."
                    >

                    <div v-if="loading" class="loading">Загрузка...</div>

                    <div v-else-if="tab === 'drivers'">
                        <table>
                            <thead>
                                <tr>
                                    <th>VK ID</th>
                                    <th>Имя</th>
                                    <th>Телефон</th>
                                    <th>Город</th>
                                    <th>Авто</th>
                                    <th>Госномер</th>
                                    <th>Поездок</th>
                                    <th>Баланс</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr v-for="driver in filteredDrivers" :key="driver.VK">
                                    <td>{{ driver.VK }}</td>
                                    <td>{{ driver.name }}</td>
                                    <td>{{ driver.phone }}</td>
                                    <td>{{ driver.city }}</td>
                                    <td>{{ driver.auto }} {{ driver.color }}</td>
                                    <td>{{ driver.state_number }}</td>
                                    <td>{{ driver.quantity }}</td>
                                    <td><strong>{{ driver.balance }} ₽</strong></td>
                                </tr>
                            </tbody>
                        </table>
                    </div>

                    <div v-else-if="tab === 'passangers'">
                        <table>
                            <thead>
                                <tr>
                                    <th>VK ID</th>
                                    <th>Имя</th>
                                    <th>Телефон</th>
                                    <th>Город</th>
                                    <th>Поездок</th>
                                    <th>Баланс</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr v-for="pass in filteredPassangers" :key="pass.VK">
                                    <td>{{ pass.VK }}</td>
                                    <td>{{ pass.name }}</td>
                                    <td>{{ pass.phone }}</td>
                                    <td>{{ pass.city }}</td>
                                    <td>{{ pass.quantity }}</td>
                                    <td><strong>{{ pass.balance }} ₽</strong></td>
                                </tr>
                            </tbody>
                        </table>
                    </div>

                    <div v-else-if="tab === 'orders'">
                        <table>
                            <thead>
                                <tr>
                                    <th>Ключ</th>
                                    <th>От</th>
                                    <th>Водитель</th>
                                    <th>Активен</th>
                                    <th>В поездке</th>
                                    <th>Локация</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr v-for="order in orders" :key="order.key">
                                    <td><code>{{ order.key.substring(0, 10) }}...</code></td>
                                    <td>{{ order.from_id }}</td>
                                    <td>{{ order.driver_id }}</td>
                                    <td>{{ order.active ? '✅' : '❌' }}</td>
                                    <td>{{ order.in_drive ? '🚗' : '⏸' }}</td>
                                    <td>{{ order.location || '-' }}</td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        </div>

        <script>
            const { createApp } = Vue;

            createApp({
                data() {
                    return {
                        tab: 'drivers',
                        search: '',
                        drivers: [],
                        passangers: [],
                        orders: [],
                        loading: false,
                        error: null
                    }
                },
                computed: {
                    filteredDrivers() {
                        if (!this.search) return this.drivers;
                        const s = this.search.toLowerCase();
                        return this.drivers.filter(d => 
                            (d.name && d.name.toLowerCase().includes(s)) ||
                            (d.phone && d.phone.toLowerCase().includes(s)) ||
                            (d.city && d.city.toLowerCase().includes(s)) ||
                            String(d.VK).includes(s)
                        );
                    },
                    filteredPassangers() {
                        if (!this.search) return this.passangers;
                        const s = this.search.toLowerCase();
                        return this.passangers.filter(p => 
                            (p.name && p.name.toLowerCase().includes(s)) ||
                            (p.phone && p.phone.toLowerCase().includes(s)) ||
                            (p.city && p.city.toLowerCase().includes(s)) ||
                            String(p.VK).includes(s)
                        );
                    },
                    activeOrders() {
                        return this.orders.filter(o => o.active).length;
                    },
                    totalTrips() {
                        return this.drivers.reduce((sum, d) => sum + (d.quantity || 0), 0) +
                               this.passangers.reduce((sum, p) => sum + (p.quantity || 0), 0);
                    }
                },
                async mounted() {
                    await this.loadData();
                    setInterval(() => this.loadData(), 30000);
                },
                methods: {
                    async loadData() {
                        this.loading = true;
                        this.error = null;
                        try {
                            const [driversRes, passangersRes, ordersRes] = await Promise.all([
                                axios.get('/api/drivers'),
                                axios.get('/api/passangers'),
                                axios.get('/api/orders')
                            ]);
                            this.drivers = driversRes.data;
                            this.passangers = passangersRes.data;
                            this.orders = ordersRes.data;
                        } catch (error) {
                            console.error('Error loading data:', error);
                            this.error = 'Ошибка загрузки данных: ' + error.message;
                        } finally {
                            this.loading = false;
                        }
                    }
                }
            }).mount('#app');
        </script>
    </body>
    </html>
    """


if __name__ == '__main__':
    import uvicorn

    uvicorn.run(app, host='0.0.0.0', port=8000)