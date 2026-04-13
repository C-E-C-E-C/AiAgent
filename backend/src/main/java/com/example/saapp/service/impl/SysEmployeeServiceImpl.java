package com.example.saapp.service.impl;

import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;
import com.example.saapp.mapper.SysEmployeeMapper;
import com.example.saapp.service.SysEmployeeService;
import com.example.saapp.vo.SysEmployee;
import org.springframework.stereotype.Service;

import java.util.List;

@Service
public class SysEmployeeServiceImpl extends ServiceImpl<SysEmployeeMapper, SysEmployee> implements SysEmployeeService {
	@Override
	public List<SysEmployee> listWithDept() {
		return baseMapper.selectEmployeeList();
	}

	@Override
	public SysEmployee getWithDeptById(Long id) {
		return baseMapper.selectEmployeeById(id);
	}
}