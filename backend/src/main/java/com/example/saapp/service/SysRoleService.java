package com.example.saapp.service;

import com.baomidou.mybatisplus.extension.service.IService;
import com.example.saapp.vo.SysMenu;
import com.example.saapp.vo.SysRole;

import java.util.List;

public interface SysRoleService extends IService<SysRole> {
    List<SysRole> listWithMenus();

    SysRole getWithMenus(Long id);

    SysRole saveWithMenus(SysRole role);

    SysRole updateWithMenus(SysRole role);

    void removeWithMenus(Long id);

    List<SysMenu> listMenus();
}