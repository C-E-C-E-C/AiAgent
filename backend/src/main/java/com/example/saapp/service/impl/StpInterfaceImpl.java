package com.example.saapp.service.impl;

import cn.dev33.satoken.stp.StpInterface;
import com.example.saapp.service.AuthCacheService;
import com.example.saapp.mapper.SysMenuMapper;
import com.example.saapp.mapper.SysUserMapper;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Component;

import java.util.ArrayList;
import java.util.LinkedHashSet;
import java.util.List;

@Component
public class StpInterfaceImpl implements StpInterface {
    @Autowired
    private SysMenuMapper menuMapper;

    @Autowired
    private SysUserMapper sysUserMapper;

    @Autowired
    private AuthCacheService authCacheService;

    // 返回用户权限列表
    @Override
    public List<String> getPermissionList(Object loginId, String loginType) {
        Long userId = Long.parseLong(loginId.toString());
        List<String> cachedPerms = authCacheService.getCachedPerms(userId);
        if (cachedPerms != null) {
            return cachedPerms;
        }

        List<String> perms = new ArrayList<>(menuMapper.selectPermsByUserId(userId) == null
                ? new ArrayList<>()
                : menuMapper.selectPermsByUserId(userId));
        List<String> roleCodes = sysUserMapper.selectRoleCodesByUserId(userId);

        if (roleCodes.contains("admin")) {
            perms.add("sys:user:list");
            perms.add("sys:user:add");
            perms.add("sys:user:edit");
            perms.add("sys:user:remove");
        }

        List<String> uniquePerms = new ArrayList<>(new LinkedHashSet<>(perms));
        authCacheService.cachePerms(userId, uniquePerms);

        return uniquePerms;
    }


    //返回角色列表
    @Override
    public List<String> getRoleList(Object loginId, String loginType) {
        Long userId = Long.parseLong(loginId.toString());
        List<String> cachedRoles = authCacheService.getCachedRoles(userId);
        if (cachedRoles != null) {
            return cachedRoles;
        }

        List<String> roles = sysUserMapper.selectRoleCodesByUserId(userId);
        authCacheService.cacheRoles(userId, roles);
        return roles;
    }
}
