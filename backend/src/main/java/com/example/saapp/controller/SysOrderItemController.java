package com.example.saapp.controller;

import cn.dev33.satoken.annotation.SaCheckPermission;
import com.example.saapp.service.SysOrderItemService;
import com.example.saapp.vo.SysOrderItem;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/order-item")
public class SysOrderItemController {

    @Autowired
    private SysOrderItemService orderItemService;

    @SaCheckPermission("order:list")
    @GetMapping("/list")
    public List<SysOrderItem> list() {
        return orderItemService.list();
    }

    @SaCheckPermission("order:add")
    @PostMapping("/add")
    public String add(@RequestBody SysOrderItem item) {
        orderItemService.save(item);
        return "添加成功";
    }

    @SaCheckPermission("order:edit")
    @PostMapping("/edit")
    public String edit(@RequestBody SysOrderItem item) {
        orderItemService.updateById(item);
        return "修改成功";
    }

    @SaCheckPermission("order:remove")
    @GetMapping("/remove/{id}")
    public String remove(@PathVariable Long id) {
        orderItemService.removeById(id);
        return "删除成功";
    }
}