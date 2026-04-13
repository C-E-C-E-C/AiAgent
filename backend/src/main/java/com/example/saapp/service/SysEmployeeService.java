package com.example.saapp.service;

import com.baomidou.mybatisplus.extension.service.IService;
import com.example.saapp.vo.SysEmployee;

import java.util.List;

public interface SysEmployeeService extends IService<SysEmployee> {
	List<SysEmployee> listWithDept();

	SysEmployee getWithDeptById(Long id);
}