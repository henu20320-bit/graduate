<template>
  <div class="app-layout">
    <header class="app-topbar">
      <div class="app-brand">
        <div class="app-brand-badge">YOLOv8</div>
        <div>
          <h1 class="app-brand-title">鸟类智能观测与预警平台</h1>
          <p class="app-brand-subtitle">围绕检测、预警、记录和统计展示构建的毕业设计系统原型</p>
        </div>
      </div>

      <nav class="app-nav">
        <router-link to="/" class="app-nav-link" exact-active-class="is-active">仪表盘</router-link>
        <router-link to="/records" class="app-nav-link" active-class="is-active">检测记录</router-link>
        <router-link to="/alerts" class="app-nav-link" active-class="is-active">预警记录</router-link>
      </nav>
    </header>

    <router-view />
  </div>
</template>
