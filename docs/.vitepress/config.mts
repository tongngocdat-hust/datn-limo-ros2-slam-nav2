import { defineConfig } from 'vitepress'

export default defineConfig({
  title: 'LIMO Dev Docs',
  description: 'Tài liệu dev cho Navigation2, SLAM và đo kiểm trên LIMO ROS 2 Humble',
  lang: 'vi-VN',
  cleanUrls: true,
  lastUpdated: true,
  themeConfig: {
    logo: '/logo.svg',
    nav: [
      { text: 'Bắt đầu', link: '/getting-started' },
      { text: 'Workflow', link: '/workflows/slam' },
      { text: 'Lệnh nhanh', link: '/reference/commands' }
    ],
    sidebar: [
      {
        text: 'Tổng quan',
        items: [
          { text: 'Trang chủ', link: '/' },
          { text: 'Bắt đầu', link: '/getting-started' },
          { text: 'Kiến trúc repo', link: '/architecture' }
        ]
      },
      {
        text: 'Workflow dev',
        items: [
          { text: 'Thí nghiệm SLAM', link: '/workflows/slam' },
          { text: 'Navigation2', link: '/workflows/nav2' },
          { text: 'Đo navigation tự động', link: '/workflows/navigation-metrics' }
        ]
      },
      {
        text: 'Tham chiếu',
        items: [
          { text: 'Lệnh nhanh', link: '/reference/commands' }
        ]
      }
    ],
    search: {
      provider: 'local'
    },
    outline: {
      label: 'Trong trang',
      level: [2, 3]
    },
    docFooter: {
      prev: 'Trang trước',
      next: 'Trang sau'
    },
    lastUpdated: {
      text: 'Cập nhật lần cuối'
    },
    footer: {
      message: 'AgileX LIMO - ROS 2 Humble research toolkit',
      copyright: 'Maintained for internal development and experiment reproducibility.'
    }
  }
})
