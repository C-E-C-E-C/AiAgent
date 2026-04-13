package com.example.saapp.controller;

import cn.dev33.satoken.annotation.SaCheckPermission;
import com.example.saapp.service.SysUserService;
import com.example.saapp.vo.SysUser;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;
import java.util.List;

@RestController
@RequestMapping("/user")
public class UserController {

    @Autowired
    private SysUserService userService;

    // 1. 用户列表
    @SaCheckPermission("sys:user:list")
    @GetMapping("/list")
    public List<SysUser> list() {
        return userService.listWithRelation();
    }

    // 2. 根据ID查询
    @SaCheckPermission("sys:user:list")
    @GetMapping("/get/{id}")
    public SysUser get(@PathVariable Long id) {
        return userService.getWithRelation(id);
    }

    // 3. 新增用户
    @SaCheckPermission("sys:user:add")
    @PostMapping("/add")
    public String add(@RequestBody SysUser user) {
        userService.saveOrUpdateEncrypt(user);
        return "添加成功";
    }

    // 4. 修改用户
    @SaCheckPermission("sys:user:edit")
    @PostMapping("/edit")
    public String edit(@RequestBody SysUser user) {
        userService.saveOrUpdateEncrypt(user);
        return "修改成功";
    }

    // 5. 删除用户
    @SaCheckPermission("sys:user:remove")
    @GetMapping("/remove/{id}")
    public String remove(@PathVariable Long id) {
        userService.removeWithRelation(id);
        return "删除成功";
    }
}