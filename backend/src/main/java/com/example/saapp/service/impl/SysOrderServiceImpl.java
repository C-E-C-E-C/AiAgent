package com.example.saapp.service.impl;

import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;
import com.example.saapp.mapper.SysOrderMapper;
import com.example.saapp.service.SysOrderService;
import com.example.saapp.vo.SysOrder;
import org.springframework.stereotype.Service;

@Service
public class SysOrderServiceImpl extends ServiceImpl<SysOrderMapper, SysOrder> implements SysOrderService {
}