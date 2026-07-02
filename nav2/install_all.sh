#!/usr/bin/env bash
set -euo pipefail

echo "[nav2] Installing ROS 2 Humble Nav2 dependencies..."

sudo apt update
sudo apt install -y \
  ros-humble-navigation2 \
  ros-humble-nav2-bringup \
  ros-humble-nav2-map-server \
  ros-humble-nav2-amcl \
  ros-humble-nav2-lifecycle-manager \
  ros-humble-nav2-planner \
  ros-humble-nav2-navfn-planner \
  ros-humble-nav2-controller \
  ros-humble-nav2-regulated-pure-pursuit-controller \
  ros-humble-nav2-behaviors \
  ros-humble-nav2-bt-navigator \
  ros-humble-nav2-waypoint-follower \
  ros-humble-nav2-velocity-smoother \
  ros-humble-nav2-smoother \
  ros-humble-dwb-core \
  ros-humble-dwb-plugins \
  ros-humble-dwb-critics \
  ros-humble-tf2-tools \
  ros-humble-tf-transformations \
  ros-humble-rviz2

echo "[nav2] Done."
echo "[nav2] If apt shows an OSRF key error, fix the ROS apt key first, then run this script again."
