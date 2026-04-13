package com.example.saapp.service.impl;

import cn.dev33.satoken.stp.StpUtil;
import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;
import com.example.saapp.mapper.SysUserRoleMapper;
import com.example.saapp.mapper.SysMenuMapper;
import com.example.saapp.mapper.SysRoleMapper;
import com.example.saapp.mapper.SysRoleMenuMapper;
import com.example.saapp.service.AuthCacheService;
import com.example.saapp.service.SysRoleService;
import com.example.saapp.vo.SysMenu;
import com.example.saapp.vo.SysRole;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.transaction.support.TransactionSynchronization;
import org.springframework.transaction.support.TransactionSynchronizationManager;

import java.util.ArrayList;
import java.util.List;

@Service
public class SysRoleServiceImpl extends ServiceImpl<SysRoleMapper, SysRole> implements SysRoleService {
    @Autowired
    private SysRoleMenuMapper roleMenuMapper;

    @Autowired
    private SysMenuMapper sysMenuMapper;

    @Autowired
    private SysUserRoleMapper sysUserRoleMapper;

    @Autowired
    private AuthCacheService authCacheService;

    @Override
    public List<SysRole> listWithMenus() {
        List<SysRole> roles = list();
        for (SysRole role : roles) {
            role.setMenuIds(roleMenuMapper.selectMenuIdsByRoleId(role.getId()));
        }
        return roles;
    }

    @Override
    public SysRole getWithMenus(Long id) {
        SysRole role = getById(id);
        if (role != null) {
            role.setMenuIds(roleMenuMapper.selectMenuIdsByRoleId(id));
        }
        return role;
    }

    @Transactional(rollbackFor = Exception.class)
    @Override
    public SysRole saveWithMenus(SysRole role) {
        save(role);
        syncRoleMenus(role.getId(), role.getMenuIds());
        return getWithMenus(role.getId());
    }

    @Transactional(rollbackFor = Exception.class)
    @Override
    public SysRole updateWithMenus(SysRole role) {
        updateById(role);
        syncRoleMenus(role.getId(), role.getMenuIds());
        invalidateUsersByRoleAfterCommit(role.getId());
        return getWithMenus(role.getId());
    }

    @Transactional(rollbackFor = Exception.class)
    @Override
    public void removeWithMenus(Long id) {
        List<Long> userIds = sysUserRoleMapper.selectUserIdsByRoleId(id);
        roleMenuMapper.deleteByRoleId(id);
        removeById(id);
        invalidateUsersAfterCommit(userIds);
    }

    @Override
    public List<SysMenu> listMenus() {
        return sysMenuMapper.selectList(null);
    }

    private void syncRoleMenus(Long roleId, List<Long> menuIds) {
        roleMenuMapper.deleteByRoleId(roleId);
        if (menuIds == null || menuIds.isEmpty()) {
            return;
        }

        for (Long menuId : new ArrayList<>(menuIds)) {
            roleMenuMapper.insertRoleMenu(roleId, menuId);
        }
    }

    private void invalidateUsersByRoleAfterCommit(Long roleId) {
        invalidateUsersAfterCommit(sysUserRoleMapper.selectUserIdsByRoleId(roleId));
    }

    private void invalidateUsersAfterCommit(List<Long> userIds) {
        if (userIds == null || userIds.isEmpty()) {
            return;
        }

        Runnable action = () -> {
            authCacheService.evictUsers(userIds);
            for (Long userId : userIds) {
                StpUtil.kickout(userId);
            }
        };

        if (TransactionSynchronizationManager.isSynchronizationActive()) {
            TransactionSynchronizationManager.registerSynchronization(new TransactionSynchronization() {
                @Override
                public void afterCommit() {
                    action.run();
                }
            });
            return;
        }

        action.run();
    }
}