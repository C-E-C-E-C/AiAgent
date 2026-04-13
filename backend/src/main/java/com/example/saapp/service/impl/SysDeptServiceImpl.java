package com.example.saapp.service.impl;

import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;
import com.example.saapp.mapper.SysDeptMapper;
import com.example.saapp.service.SysDeptService;
import com.example.saapp.vo.SysDept;
import org.springframework.stereotype.Service;

@Service
public class SysDeptServiceImpl extends ServiceImpl<SysDeptMapper, SysDept> implements SysDeptService {
}