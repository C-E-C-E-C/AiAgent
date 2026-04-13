package com.example.saapp.controller;

import cn.dev33.satoken.annotation.SaCheckRole;
import com.example.saapp.service.SysRoleService;
import com.example.saapp.vo.SysMenu;
import com.example.saapp.vo.SysRole;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/role")
@SaCheckRole("admin")
public class SysRoleController {

    @Autowired
    private SysRoleService roleService;

    @GetMapping("/list")
    public List<SysRole> list() {
        return roleService.listWithMenus();
    }

    @GetMapping("/{id}")
    public SysRole get(@PathVariable Long id) {
        return roleService.getWithMenus(id);
    }

    @PostMapping("/add")
    public SysRole add(@RequestBody SysRole role) {
        return roleService.saveWithMenus(role);
    }

    @PostMapping("/edit")
    public SysRole edit(@RequestBody SysRole role) {
        return roleService.updateWithMenus(role);
    }

    @GetMapping("/remove/{id}")
    public String remove(@PathVariable Long id) {
        roleService.removeWithMenus(id);
        return "删除成功";
    }

    @GetMapping("/menus")
    public List<SysMenu> menus() {
        return roleService.listMenus();
    }
}