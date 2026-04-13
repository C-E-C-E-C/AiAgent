package com.example.saapp.controller;

import cn.dev33.satoken.annotation.SaCheckPermission;
import com.example.saapp.service.SysEmployeeService;
import com.example.saapp.vo.SysEmployee;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/employee")
public class SysEmployeeController {

    @Autowired
    private SysEmployeeService employeeService;

    @SaCheckPermission("employee:list")
    @GetMapping("/list")
    public List<SysEmployee> list() {
        return employeeService.listWithDept();
    }

    @SaCheckPermission("employee:list")
    @GetMapping("/get/{id}")
    public SysEmployee get(@PathVariable Long id) {
        return employeeService.getWithDeptById(id);
    }

    @SaCheckPermission("employee:add")
    @PostMapping("/add")
    public String add(@RequestBody SysEmployee employee) {
        employeeService.save(employee);
        return "添加成功";
    }

    @SaCheckPermission("employee:edit")
    @PostMapping("/edit")
    public String edit(@RequestBody SysEmployee employee) {
        employeeService.updateById(employee);
        return "修改成功";
    }

    @SaCheckPermission("employee:remove")
    @GetMapping("/remove/{id}")
    public String remove(@PathVariable Long id) {
        employeeService.removeById(id);
        return "删除成功";
    }
}