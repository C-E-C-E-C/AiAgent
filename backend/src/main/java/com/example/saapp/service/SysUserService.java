package com.example.saapp.service;

import com.baomidou.mybatisplus.extension.service.IService;
import com.example.saapp.vo.SysUser;

import java.util.List;

public interface SysUserService extends IService<SysUser> {
    boolean saveOrUpdateEncrypt(SysUser user);

    List<SysUser> listWithRelation();

    SysUser getWithRelation(Long id);

    boolean removeWithRelation(Long id);


}