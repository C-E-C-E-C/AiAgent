package com.example.saapp.controller;

import cn.dev33.satoken.annotation.SaCheckPermission;
import com.example.saapp.service.SysOrderService;
import com.example.saapp.vo.SysOrder;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/order")
public class SysOrderController {

    @Autowired
    private SysOrderService orderService;

    @SaCheckPermission("order:list")
    @GetMapping("/list")
    public List<SysOrder> list() {
        return orderService.list();
    }

    @SaCheckPermission("order:list")
    @GetMapping("/get/{id}")
    public SysOrder get(@PathVariable Long id) {
        return orderService.getById(id);
    }

    @SaCheckPermission("order:add")
    @PostMapping("/add")
    public String add(@RequestBody SysOrder order) {
        orderService.save(order);
        return "添加成功";
    }

    @SaCheckPermission("order:edit")
    @PostMapping("/edit")
    public String edit(@RequestBody SysOrder order) {
        orderService.updateById(order);
        return "修改成功";
    }

    @SaCheckPermission("order:remove")
    @GetMapping("/remove/{id}")
    public String remove(@PathVariable Long id) {
        orderService.removeById(id);
        return "删除成功";
    }
}