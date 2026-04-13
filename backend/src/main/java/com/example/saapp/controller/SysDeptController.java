package com.example.saapp.controller;

import cn.dev33.satoken.annotation.SaCheckPermission;
import com.example.saapp.service.SysDeptService;
import com.example.saapp.vo.SysDept;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/dept")
public class SysDeptController {

    @Autowired
    private SysDeptService deptService;

    @SaCheckPermission("dept:list")
    @GetMapping("/list")
    public List<SysDept> list() {
        return deptService.list();
    }

    @SaCheckPermission("dept:list")
    @GetMapping("/get/{id}")
    public SysDept get(@PathVariable Long id) {
        return deptService.getById(id);
    }

    @SaCheckPermission("dept:add")
    @PostMapping("/add")
    public String add(@RequestBody SysDept dept) {
        deptService.save(dept);
        return "添加成功";
    }

    @SaCheckPermission("dept:edit")
    @PostMapping("/edit")
    public String edit(@RequestBody SysDept dept) {
        deptService.updateById(dept);
        return "修改成功";
    }

    @SaCheckPermission("dept:remove")
    @GetMapping("/remove/{id}")
    public String remove(@PathVariable Long id) {
        deptService.removeById(id);
        return "删除成功";
    }
}