package com.example.saapp.service.impl;

import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;
import com.example.saapp.mapper.SysOrderItemMapper;
import com.example.saapp.service.SysOrderItemService;
import com.example.saapp.vo.SysOrderItem;
import org.springframework.stereotype.Service;

@Service
public class SysOrderItemServiceImpl extends ServiceImpl<SysOrderItemMapper, SysOrderItem> implements SysOrderItemService {
}