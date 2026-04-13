<script setup>
import { ref } from 'vue';

// 获得大模型生成的旅行规划
import { planTrip } from '../api/LLMPython';

import { onMounted } from 'vue';

const map = ref(null);
const markers = ref([]);

const message = ref('');
const loading = ref(false);
const mapData = ref(null);
const tripResult = ref(null);
const pointList = ref([]);

const address = ref('杭州');
const days = ref(3);
const budget = ref(500);
const preferences = ref('喜欢美食');

const GEOCODE_INTERVAL_MS = 200;
let lastGeocodeAt = 0;
let geocodeQueue = Promise.resolve();

const wait = (ms) => new Promise(resolve => setTimeout(resolve, ms));

const throttleGeocode = () => {
    const run = geocodeQueue.then(async () => {
        const now = Date.now();
        const waitMs = Math.max(0, lastGeocodeAt + GEOCODE_INTERVAL_MS - now);
        if (waitMs > 0) {
            await wait(waitMs);
        }
        lastGeocodeAt = Date.now();
    });

    geocodeQueue = run.catch(() => {});
    return run;
};

const geocodePointByText = async (point) => {
    const addressText = String(point?.subtitle || point?.address || point?.title || address.value || '').trim();
    const cityText = String(point?.city || mapData.value?.city || address.value || '').trim();

    if (!addressText) {
        return null;
    }
    console.log('addresstext',addressText);
    console.log('citytext',cityText);

    await throttleGeocode();
    
    
    const url = `https://restapi.amap.com/v5/place/text?keywords=${encodeURIComponent(addressText)}&region=${encodeURIComponent(cityText)}&output=JSON&key=360124fae15c16eaf0825e822431f1fd`;
    const response = await fetch(url);
    console.log('response:',response);
    
    const data = await response.json();
    console.log('data:',data);
    const geocode = data?.pois?.[0];
    console.log('gencode',geocode);
    

    if (!geocode?.location) {
        return null;
    }

    const [lng, lat] = String(geocode.location).split(',').map(item => Number(item));
    if (Number.isNaN(lng) || Number.isNaN(lat)) {
        return null;
    }

    return {
        ...point,
        lng,
        lat,
        geocodeAddress: addressText,
        geocodeCity: cityText,
        geocodeProvince: geocode.province || point?.province || '',
        geocodeDistrict: geocode.district || point?.district || '',
        geocodeLevel: geocode.level || '',
        geocodeRaw: geocode,
    };
};

const normalizePoint = (point, index = 0) => {
    console.log('原始路线点数据:', index, point);

    const normalizedPoint = {
        day: Number(point?.day ?? index + 1),
        title: String(point?.title ?? point?.name ?? `地点 ${index + 1}`),
        subtitle: String(point?.subtitle ?? ''),
        address: String(point?.subtitle ?? ''),
        time: String(point?.time ?? ''),
        note: String(point?.note ?? ''),
        province: String(point?.province ?? ''),
        city: String(point?.city ?? ''),
        district: String(point?.district ?? ''),
        lng: Number(point?.lng),
        lat: Number(point?.lat),
    };

    console.log('标准化后的路线点数据:', index, normalizedPoint);

    return normalizedPoint;
};

console.log('loding状态',loading.value);


const getMapData = async () => {
    try {
        const response = await fetch('https://restapi.amap.com/v5/place/text?address=杭州&output=JSON&key=360124fae15c16eaf0825e822431f1fd');
        console.log("地图数据:",response);
        message.value = JSON.stringify(response);
        
        const data = await response.json();
        console.log("地图数据:",data);
        console.log("地图数据:",data.geocodes);
        mapData.value = data.geocodes[0];
    }catch(error){
        console.error('Error fetching map data:', error);
    }
};



const getTripPlan = async () => {
    loading.value = true
    try{
        const data = await planTrip({
            destination: address.value,
            days: days.value,
            budget : budget.value,
            preferences : preferences.value
        })

        console.log('旅行规划:', data);
        tripResult.value = data;

        const normalizedPoints = Array.isArray(data?.route_points)
            ? data.route_points.map((point, index) => normalizePoint(point, index)).filter(Boolean)
            : [];

        const geocodedPoints = [];
        for (const point of normalizedPoints) {
            const resolvedPoint = await geocodePointByText(point);
            if (resolvedPoint) {
                geocodedPoints.push(resolvedPoint);
            } else if (!Number.isNaN(point.lng) && !Number.isNaN(point.lat)) {
                geocodedPoints.push(point);
            }
        }

        pointList.value = geocodedPoints;

        if (map.value && pointList.value.length > 0) {
            const firstPoint = pointList.value[0];
            map.value.setCenter([firstPoint.lng, firstPoint.lat]);
        }

        renderAllMarkers();

    }catch(error){
        console.log("大模型返回失败");
    }finally{
        loading.value = false
    }
};
// 绘制标记点
const createMarkerContent = (index) => {
    const markerEl = document.createElement('div');
    markerEl.className = 'map-seq-marker';
    markerEl.innerHTML = `<span>${index + 1}</span>`;
    return markerEl;
};

const renderAllMarkers = ()=>{
    if(!map.value){
        console.log('没有进入绘制标记点流程');
        
        return ;
    }

    // 清除之前的标记
    markers.value.forEach(m => {
        m.setMap(null);
    });
    markers.value = [];

    pointList.value.forEach((point, index) => {
        const newMarker = new AMap.Marker({
            position: [point.lng, point.lat],
            map: map.value,
            title: point.address || point.title,
            content: createMarkerContent(index),
            offset: new AMap.Pixel(-14, -14),
        });
        markers.value.push(newMarker);
    });
        
}

onMounted(() => {
    //初始化地图
    map.value = new AMap.Map('mapContainer', {
        resizeEnable : true,
        center: [120.15507, 30.27415], // 初始中心点坐标（杭州）
        zoom: 10, // 初始缩放级别
    });

    console.log('onMounted');
    getMapData();
    renderAllMarkers()    // getTripPlan();
});


</script>

<template>
    <div class="travel-page">
        <header class="top-toolbar">
            <div class="toolbar-title">
                <div class="eyebrow">Travel Planner</div>
                <h1>智能旅行地图</h1>
                <p>输入目的地和旅行偏好，生成路线点并直接绘制到地图上。</p>
            </div>

            <div class="toolbar-form">
                <label class="toolbar-field">
                    <span>目的地</span>
                    <input type="text" v-model="address" placeholder="请输入目的地">
                </label>
                <label class="toolbar-field">
                    <span>天数</span>
                    <input type="text" v-model="days" placeholder="天数">
                </label>
                <label class="toolbar-field">
                    <span>预算</span>
                    <input type="text" v-model="budget" placeholder="预算">
                </label>
                <label class="toolbar-field">
                    <span>偏好</span>
                    <input type="text" v-model="preferences" placeholder="偏好">
                </label>
                <div class="toolbar-actions">
                    <button class="btn primary" @click="getTripPlan">
                        <span v-if="loading" class="btn-spinner"></span>
                        <span>{{ loading ? '生成中...' : '获取旅行规划' }}</span>
                    </button>
                    <button class="btn ghost" @click="getMapData">定位城市</button>
                </div>
            </div>
        </header>

        <section class="content-grid">
            <aside class="left-panel">
                <div class="summary-grid">
                    <div class="stat-card">
                        <span>路线点</span>
                        <strong>{{ pointList.length }}</strong>
                    </div>
                    <div class="stat-card">
                        <span>城市</span>
                        <strong>{{ address || '未定位' }}</strong>
                    </div>
                </div>

                <div class="result-card">
                    <div class="section-title">景点卡片</div>
                    <div class="spot-list">
                        <div v-for="(item, index) in pointList" :key="`${item.title}-${index}`" class="spot-card">
                            <div class="spot-top">
                                <div>
                                    <div class="spot-day">Day {{ item.day }}</div>
                                    <h3>{{ item.title }}</h3>
                                </div>
                                <span class="spot-time">{{ item.time || '未设置时间' }}</span>
                            </div>
                            <p class="spot-subtitle">{{ item.subtitle || '暂无副标题' }}</p>
                            <p class="spot-address">地址：{{ item.address || '暂无地址' }}</p>
                            <p class="spot-city">城市：{{ item.city || '暂无城市' }}</p>
                            <p class="spot-note">{{ item.note || '暂无备注' }}</p>
                            <div class="spot-meta">
                                <span>{{ item.lng }}</span>
                                <span>{{ item.lat }}</span>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- <div class="debug-card">
                    <div class="section-title">规划结果</div>
                    <pre>{{ tripResult }}</pre>
                </div> -->
            </aside>

            <main class="map-panel">

                <div v-if="loading" class="loading-overlay">
                    <p>正在生成旅行规划...</p>   
                   

                </div>
                <!-- <div class="map-header">
                    <div>
                        <div class="section-title">地图预览</div>
                        <p>将生成的路线点自动居中并绘制到地图中。</p>
                    </div>
                    <div class="badge">{{ 杭州 || address }}</div>
                </div> -->

                 <div id="mapContainer" class="map-box" v-show="!loading"></div>
                
                <!-- <div class="debug-card">
                    <div class="section-title">调试信息</div>
                    <div class="debug-item">地图数据：{{ message }}</div>
                    <div class="debug-item">经纬度：{{ mapData?.location }}</div>
                </div> -->
            </main>
        </section>
    </div>
</template>

<style scoped>
.travel-page {
    min-height: 100vh;
    padding: 20px;
    display: flex;
    flex-direction: column;
    gap: 18px;
    background:
        radial-gradient(circle at top left, rgba(59, 130, 246, 0.18), transparent 28%),
        radial-gradient(circle at bottom right, rgba(16, 185, 129, 0.16), transparent 24%),
        linear-gradient(180deg, #f8fbff 0%, #eef4ff 100%);
    box-sizing: border-box;
}

.btn-loading {
display: inline-flex;
align-items: center;
justify-content: center;
gap: 8px;
}

.btn:disabled {
cursor: not-allowed;
opacity: 0.72;
filter: saturate(0.85);
}

.btn:disabled:hover {
transform: none;
}

.btn:disabled {
animation: btnPulse 1.2s ease-in-out infinite;
}

.btn-spinner {
width: 14px;
height: 14px;
border-radius: 50%;
border: 2px solid rgba(255, 255, 255, 0.35);
border-top-color: #ffffff;
animation: spin 0.8s linear infinite;
}

@keyframes btnPulse {
0%, 100% {
box-shadow: 0 14px 28px rgba(37, 99, 235, 0.22);
}
50% {
box-shadow: 0 14px 28px rgba(37, 99, 235, 0.34);
}
}

@keyframes spin {
to {
transform: rotate(360deg);
}
}

.top-toolbar,
.content-grid {
    display: flex;
    gap: 18px;
}

.top-toolbar {
    flex-wrap: wrap;
    align-items: stretch;
    justify-content: space-between;
}

.toolbar-title,
.toolbar-form,
.left-panel,
.map-panel {
    display: flex;
    flex-direction: column;
    gap: 16px;
}

.left-panel {
    flex: 0 0 360px;
    max-width: 360px;
}

.map-panel {
    flex: 1 1 auto;
    min-width: 0;
}

.toolbar-title {
    flex: 1 1 280px;
    min-width: 280px;
    padding: 22px;
    border-radius: 20px;
    box-shadow: 0 18px 40px rgba(15, 23, 42, 0.08);
}

.toolbar-form {
    flex: 2 1 680px;
    min-width: 320px;
    padding: 18px;
    border-radius: 20px;
    background: rgba(255, 255, 255, 0.82);
    border: 1px solid rgba(148, 163, 184, 0.18);
    box-shadow: 0 18px 40px rgba(15, 23, 42, 0.08);
    backdrop-filter: blur(16px);
    display: grid;
    grid-template-columns: repeat(4, minmax(0, 1fr));
    gap: 14px;
    align-items: end;
}

.hero-card,
.stat-card,
.result-card,
.debug-card,
.map-box {
    background: rgba(255, 255, 255, 0.82);
    border: 1px solid rgba(148, 163, 184, 0.18);
    border-radius: 20px;
    box-shadow: 0 18px 40px rgba(15, 23, 42, 0.08);
    backdrop-filter: blur(16px);
}

.toolbar-title {
    background: linear-gradient(135deg, rgba(37, 99, 235, 0.92), rgba(20, 184, 166, 0.88));
    color: #fff;
}

.eyebrow {
    display: inline-block;
    padding: 6px 10px;
    border-radius: 999px;
    background: rgba(255, 255, 255, 0.16);
    font-size: 12px;
    letter-spacing: 0.12em;
    text-transform: uppercase;
}

.toolbar-title h1 {
    margin: 14px 0 10px;
    font-size: 30px;
    line-height: 1.1;
}

.toolbar-title p {
    margin: 0;
    line-height: 1.8;
    color: rgba(255, 255, 255, 0.92);
}

.toolbar-field {
    display: grid;
    gap: 8px;
    color: #334155;
    font-size: 14px;
    font-weight: 600;
}

.toolbar-field input {
    width: 100%;
    box-sizing: border-box;
    padding: 12px 14px;
    border: 1px solid #dbe4f0;
    border-radius: 14px;
    outline: none;
    background: rgba(248, 250, 252, 0.92);
    color: #0f172a;
    transition: border-color 0.2s ease, box-shadow 0.2s ease, transform 0.2s ease;
}

.toolbar-field input:focus {
    border-color: #2563eb;
    box-shadow: 0 0 0 4px rgba(37, 99, 235, 0.12);
    transform: translateY(-1px);
}

.toolbar-actions {
    grid-column: 1 / -1;
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 10px;
}

.btn {
    border: none;
    border-radius: 14px;
    padding: 12px 14px;
    font-weight: 700;
    cursor: pointer;
    transition: transform 0.2s ease, box-shadow 0.2s ease, filter 0.2s ease;
}

.btn:hover {
    transform: translateY(-1px);
}

.btn.primary {
    background: linear-gradient(135deg, #2563eb, #0ea5e9);
    color: #fff;
    box-shadow: 0 14px 28px rgba(37, 99, 235, 0.22);
}

.btn.ghost {
    background: rgba(15, 23, 42, 0.04);
    color: #0f172a;
    border: 1px solid #dbe4f0;
}

.summary-grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 14px;
}

.stat-card {
    padding: 16px;
    display: grid;
    gap: 8px;
}

.stat-card span,
.map-header p,
.debug-item,
.result-card pre {
    color: #64748b;
}

.stat-card strong {
    color: #0f172a;
    font-size: 22px;
}

.result-card,
.debug-card {
    padding: 18px;
}

.spot-list {
    display: grid;
    gap: 12px;
    max-height: 420px;
    overflow: auto;
    padding-right: 4px;
}

.spot-card {
    padding: 14px;
    border-radius: 16px;
    border: 1px solid rgba(148, 163, 184, 0.16);
    background: linear-gradient(180deg, #ffffff 0%, #f8fbff 100%);
    display: grid;
    gap: 10px;
    box-shadow: 0 10px 24px rgba(15, 23, 42, 0.06);
}

.spot-top {
    display: flex;
    justify-content: space-between;
    gap: 12px;
    align-items: flex-start;
}

.spot-day {
    display: inline-flex;
    padding: 4px 8px;
    border-radius: 999px;
    background: rgba(37, 99, 235, 0.08);
    color: #2563eb;
    font-size: 12px;
    font-weight: 700;
    margin-bottom: 8px;
}

.spot-card h3 {
    margin: 0;
    font-size: 16px;
    color: #0f172a;
}

.spot-time {
    flex: 0 0 auto;
    font-size: 12px;
    padding: 6px 10px;
    border-radius: 999px;
    background: rgba(16, 185, 129, 0.1);
    color: #059669;
    white-space: nowrap;
}

.spot-subtitle,
.spot-note {
    margin: 0;
    line-height: 1.7;
    color: #475569;
}

.spot-address,
.spot-city {
    margin: 0;
    padding: 10px 12px;
    border-radius: 12px;
    background: rgba(20, 184, 166, 0.06);
    color: #0f766e;
    line-height: 1.7;
    font-weight: 700;
}

.spot-meta {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    font-size: 12px;
    color: #64748b;
}

.spot-meta span {
    padding: 5px 8px;
    border-radius: 999px;
    background: #f1f5f9;
}

.section-title {
    font-size: 15px;
    font-weight: 800;
    color: #0f172a;
    margin-bottom: 10px;
}

.result-card pre {
    margin: 0;
    white-space: pre-wrap;
    word-break: break-word;
    max-height: 260px;
    overflow: auto;
    line-height: 1.7;
}

.map-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 16px;
}

.map-header p {
    margin: 6px 0 0;
}

.badge {
    padding: 8px 14px;
    border-radius: 999px;
    background: rgba(37, 99, 235, 0.08);
    color: #2563eb;
    border: 1px solid rgba(37, 99, 235, 0.16);
    font-weight: 700;
}

.map-box {
    width: 100%;
    min-height: 620px;
    overflow: hidden;
}

.map-seq-marker {
    width: 28px;
    height: 28px;
    border-radius: 50%;
    background: linear-gradient(135deg, #2563eb, #0ea5e9);
    border: 2px solid #ffffff;
    box-shadow: 0 10px 20px rgba(37, 99, 235, 0.28);
    display: flex;
    align-items: center;
    justify-content: center;
    color: #fff;
    font-size: 12px;
    font-weight: 800;
    line-height: 1;
}

.map-seq-marker span {
    transform: translateY(-0.5px);
}

.debug-card {
    display: grid;
    gap: 8px;
}

.debug-item {
    font-size: 13px;
    line-height: 1.7;
}

@media (max-width: 1080px) {
    .travel-page {
        padding: 16px;
    }

    .top-toolbar,
    .content-grid {
        flex-direction: column;
    }

    .content-grid {
        align-items: stretch;
    }

    .left-panel,
    .map-panel {
        width: 100%;
            max-width: none;
            flex: 1 1 auto;
    }

    .toolbar-form {
        grid-template-columns: repeat(2, minmax(0, 1fr));
    }

    .summary-grid {
        grid-template-columns: 1fr 1fr;
    }

    .map-box {
        min-height: 520px;
    }
}

@media (max-width: 640px) {
    .travel-page {
        padding: 16px;
    }

    .toolbar-form,
    .toolbar-actions,
    .summary-grid {
        grid-template-columns: 1fr;
    }

    .map-header {
        flex-direction: column;
        align-items: flex-start;
    }
}

.loading-overlay {
    width: 100%;
    min-height: 620px;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 20px;
    background: rgba(255, 255, 255, 0.82);
    border: 1px solid rgba(148, 163, 184, 0.18);
    box-shadow: 0 18px 40px rgba(15, 23, 42, 0.08);
    backdrop-filter: blur(16px);
}

.loading-card {
    display: grid;
    justify-items: center;
    gap: 14px;
    padding: 28px 32px;
}

.loading-spinner {
    width: 44px;
    height: 44px;
    border-radius: 50%;
    border: 4px solid rgba(37, 99, 235, 0.16);
    border-top-color: #2563eb;
    animation: spin 0.9s linear infinite;
}

.loading-card p {
    margin: 0;
    color: #0f172a;
    font-weight: 600;
}

@keyframes spin {
    to {
        transform: rotate(360deg);
    }
}
</style>