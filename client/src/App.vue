<template>
  <div id="app">
    <el-container>
      <el-header>
        <h1>Print Shtrih Client</h1>
        <el-menu mode="horizontal" :default-active="activeTab" @select="handleMenuSelect">
          <el-menu-item index="checks">Чеки</el-menu-item>
          <el-menu-item index="egais">ЕГАИС</el-menu-item>
          <el-menu-item index="egais-xml">ЕГАИС XML</el-menu-item>
          <el-menu-item index="kkt">ККТ</el-menu-item>
          <el-menu-item index="logs">Логи</el-menu-item>
          <el-menu-item index="stats">Статистика</el-menu-item>
        </el-menu>
      </el-header>
      
      <el-main>
        <CheckForm v-if="activeTab === 'checks'" @check-created="handleCheckCreated" />
        <EgaisForm v-if="activeTab === 'egais'" @egais-sent="handleEgaisSent" />
        <EgaisXmlUploadForm v-if="activeTab === 'egais-xml'" />
        <KktInfo v-if="activeTab === 'kkt'" />
        <LogsView v-if="activeTab === 'logs'" />
        <StatsView v-if="activeTab === 'stats'" />
      </el-main>
    </el-container>
  </div>
</template>

<script>
import CheckForm from './components/CheckForm.vue'
import EgaisForm from './components/EgaisForm.vue'
import EgaisXmlUploadForm from './components/EgaisXmlUploadForm.vue'
import KktInfo from './components/KktInfo.vue'
import LogsView from './components/LogsView.vue'
import StatsView from './components/StatsView.vue'

export default {
  name: 'App',
  components: {
    CheckForm,
    EgaisForm,
    EgaisXmlUploadForm,
    KktInfo,
    LogsView,
    StatsView
  },
  data() {
    return {
      activeTab: 'checks'
    }
  },
  methods: {
    handleMenuSelect(key) {
      this.activeTab = key
    },
    handleCheckCreated(result) {
      this.$message.success('Чек создан: ' + result.message)
    },
    handleEgaisSent(result) {
      this.$message.success('ЕГАИС: ' + result.message)
    }
  }
}
</script>

<style>
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

.el-header {
  background-color: #409EFF;
  color: white;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.el-header h1 {
  margin: 0;
}

.el-main {
  padding: 20px;
}
</style>
